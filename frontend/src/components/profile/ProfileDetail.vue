<template>
  <div>
    <transition name="fade" mode="out-in" appear>
    
      
    <v-card
      elevation=1
      v-if="profile"
      :key="profile.id"
      class="theprofile pa-2"
    >
    <v-row>
      <v-col>
        <v-card-actions>
      <v-btn rounded color="red" small text @click="hideProfile">
        <v-icon dark>
        mdi-minus
      </v-icon>

              Clear selection
      </v-btn>
      <v-spacer></v-spacer>
    
      <v-menu offset-y>
      <template v-slot:activator="{ on, attrs }">
        <v-btn
          color="primary"
          dark
          v-bind="attrs"
          v-on="on"
        >
        <v-icon
        role="img"
        aria-label="Profile Actions" aria-hidden="false">
            {{ icons.mdiCog }}
        </v-icon>

        </v-btn>
      </template>
      <v-list>
        <v-list-item
          v-for="(item, index) in items"
          :key="index"
        >
          <v-list-item-title>
            {{ $t(item.title) }}
            </v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
    </v-card-actions>
      </v-col>
      </v-row>
    
    <v-row>
      <v-col cols="12" sm="4">
        <v-img
        v-if="hasPhoto(profile)"
        :src="showPhoto()"

        />

        <v-gravatar
        v-else
        :email="profile.email"
        :size="200"
        class="gravatar b--light-gray ba w-100"
        />    
      </v-col>
      
      <v-col cols="12" sm="8">
        <v-card-title class="pl-0">
          {{ profile.name }}
        </v-card-title>
        <v-card-subtitle class="pl-0">
         <v-icon color="primary" class="pr-2">
           {{ icons.mdiEmail }}
        </v-icon> 
         <a :href="'mailto:' + profile.email">{{ profile.email }}</a>
         
        {{ profile.phone }}
        </v-card-subtitle>
      
      </v-col>      
    </v-row>
    
    <v-row>
      <v-col>
        
        <div class="">
          <h4>
              Skills and interests
            </h4>
          <v-chip
            class="ma-1"
            color="primary"
            v-for="tag in profile.tags"
            v-bind:key="tag.name"
            :data-name="tag"
            @click.stop.prevent="toggleTag"
            >{{ tag.name }}
          </v-chip>

          <!-- TODO, make this into a tag list component -->
          <div v-if="hasActiveClusters()" class="cluster-component">
            <h4>
              {{ $t('message.profileDetail.clusterMember') }}
            </h4>

            <v-chip
              class="ma-1"
              color="primary"
              v-for="cluster in profile.clusters"
              v-bind:key="cluster.name"
              :data-name="cluster"
              @click.stop.prevent="toggleCluster"
              >{{ cluster.name }}
            </v-chip>
          </div>
          </div>
        </v-col>
      
      </v-row>
      
      <v-row v-if="this.profile.bio">
          <v-col>
             <div class="w-100 bio lh-copy measure-wide">
                <div v-html="bioOutput"></div>
            </div>
          </v-col>
      </v-row>
        
    </v-card>
    </transition>
  </div>
  
</template>

<script>
/* eslint-disable */
import Vue from 'vue'
import Gravatar from 'vue-gravatar'
import debugLib from 'debug'
import marked from 'marked'
import sanitizeHTML from 'sanitize-html'
const debug = debugLib('cl8.ProfileDetail')
Vue.component('v-gravatar', Gravatar)
import { mdiAccount, mdiEmail, mdiCog } from '@mdi/js'
import { linkify, hasPhoto } from '@/utils'

export default {
  name: 'ProfileDetail',
  components: {
    Gravatar
  },
  data() {
    return {
      icons: {
        mdiEmail,
        mdiCog
      },
      loading: false,
      showFlashMessage: false,
      flashMessage: '',
      items: [
        { title: 'message.profileDetail.resendInvite' },
        { title: 'message.shared.editProfile' },
      ],
    }
  },
  computed: {
    user() {
      return this.$store.getters.currentUser
    },
    profile() {
      return this.$store.getters.profile
    },
    activeTags() {
      return this.$store.getters.activeTags
    },
    websiteLink() {
      return this.profile.website ? linkify(this.profile.website) : null
    },
    twitterLink() {
      return this.profile.twitter
        ? linkify(this.profile.twitter, 'https://twitter.com')
        : null
    },
    facebookLink() {
      return this.profile.facebook
        ? linkify(this.profile.facebook, 'https://facebook.com')
        : null
    },
    linkedinLink() {
      return this.profile.linkedin
        ? linkify(this.profile.linkedin, 'https://linkedin.com/in')
        : null
    },
    bioOutput() {
      return this.profile.bio ? marked(sanitizeHTML(this.profile.bio)) : null
    },
    isAdmin() {
      if (this.user) {
        return !!this.user.admin
      } else{
        return false
      }

    },
    messageClassObject: function () {
      return {
        'bg-light-blue': this.flashMessageClass == 'info',
        'bg-light-red': this.flashMessageClass == 'error'
      }
    }
  },
  methods: {
    canEdit: function () {
      if (this.profile && this.user) {
        debug('can edit?', this.profile.id, this.user.id)
        return this.profile.id == this.user.id
      }
      return false
    },
    hideProfile: function (ev) {
      this.$store.dispatch('hideProfile')
      this.$router.push({ name: 'home'})
    },
    toggleTag: function (ev) {
      let tag = ev.target.textContent.trim().toLowerCase()
      this.$store.dispatch('updateActiveTags', tag)
    },
    toggleCluster: function (ev) {
      const cluster = ev.target.textContent.trim().toLowerCase()
      debug('toggleCluster', { cluster })
      this.$store.dispatch('updateActiveClusters', cluster)
    },
    hasActiveClusters: function () {
      if (this.profile.clusters) {
        return !!this.profile.clusters.length
      }
    },
    hideFlashMessage: function () {
      debug('hiding message')
      this.showFlashMessage = false
      this.flashMessage = ''
    },
    isActive: function (term) {
      if (typeof this.activeTags !== 'undefined') {
        let matchesActiveTag = this.activeTags.indexOf(term) !== -1
        return matchesActiveTag
      }
    },
    isVisible: function () {
      return this.profile.visible
    },
    hasPhoto,
    showPhoto() {
      return this.profile.detail_photo
    },
    async resendInvite() {
      debug('resendInvite', this.profile)

      const response = await this.$store
        .dispatch('resendInvite', this.profile)
        .catch((err) => {
          debug({ errMessage: err.response.data.message })
          this.flashMessage = err.response.data.message
          this.flashMessageClass = 'error'
          this.showFlashMessage = true
        })
      if (response) {
        debug({ response })
        this.flashMessage = response.data.message
        this.flashMessageClass = 'info'
        this.showFlashMessage = true
      }
    }
  },
}
</script>

<style>
ul.tags li.list {
  display: inline-block;
}
img.gravatar {
  box-shadow: 3px 3px 3px #ddd;
}

/* this only shows a border when we have two or more links in a row */
.social-links li + li {
  border-left: 1px solid #000000;
  padding-left: 1em;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.1s;
}
.fade-enter, .fade-leave-to /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
