<template>
  <div class="cf bg-white">
    <nav-header-edit />
    <div class="fl pa2">
      <div class="pa3 center w-80-l cf">
        <div>
          <form class v-if="profile">
            <div class="cf w-100" style="min-height: 11em">
              <div class="fl w-100 w-25-ns mb3">
                <router-link
                  :to="{ name: 'editProfilePhoto' }"
                  class="edithover w-80 mr4"
                >
                  <img
                    v-if="hasPhoto(profile)"
                    :src="showPhoto()"
                    class="supplied-photo b--light-silver ba w-100 v-top fn-ns"
                  />

                  <v-gravatar
                    v-else
                    :email="profile.email"
                    :size="200"
                    class="gravatar b--light-silver ba"
                  />
                </router-link>

                <div class="w-40 w-100-ns fn-ns dib v-btm mt2">
                  <div
                    class="f6 dim br2 dib w-80 white mb2"
                    v-bind:class="{
                      'bg-green': profile.visible,
                      'bg-red': !profile.visible
                    }"
                  >
                    <input
                      type="checkbox"
                      class="dib w-20 mv2 ml2"
                      id="visible-checkbox"
                      v-model="profile.visible"
                    />
                    <label
                      v-if="profile.visible"
                      for="visible-checkbox"
                      class="dib w-70"
                    >
                      {{ $t('message.shared.visible') }}
                    </label>
                    <label v-else for="visible-checkbox" class="dib w-70">
                      {{ $t('message.shared.hidden') }}
                    </label>
                  </div>
                  <p class="f6 lh-copy i gray ph2" v-if="profile.visible">
                    {{ $t('message.profileEdit.profileVisible') }}
                  </p>
                  <p class="f6 lh-copy i gray ph2" v-else>
                    {{ $t('message.profileEdit.profileHidden') }}
                  </p>
                </div>
              </div>

              <div class="fl w-100 w-75-ns mt0 pt0">
                <ul class="list mt0 pt0 f4 pa0 border-box">
                  <li class="list name">
                    <label class="f5" for>
                      {{ $t('message.profileEdit.name') }}
                      <span class="f6 lh-copy i gray">{{
                        $t('message.profileEdit.nameMessage')
                      }}</span>
                    </label>
                    <v-text-field
                      class="mt-1"
                      outlined
                      v-model="profile.name"
                    >
                    </v-text-field>
                  </li>

                  <li class="list email mt2">
                    <label class="f5" for>
                      {{ $t('message.profileEdit.email') }}
                      <span class="f6 lh-copy i gray">{{
                        $t('message.profileEdit.emailMessage')
                      }}</span>
                    </label>
                    <div class="w-100 mt1 bg-near-white pa2">
                      {{ profile.email }}
                    </div>
                  </li>
                  <li class="list phone mt2">
                    <label class="f5 mb2" for>
                      {{ $t('message.profileEdit.phone') }}
                    </label>
                    <span class="f6 lh-copy i gray">
                      {{ $t('message.profileEdit.phoneMessage') }}
                    </span>
                    <v-text-field
                      class="mt-1"
                      outlined
                      v-model="profile.phone"
                    >
                    </v-text-field>
                  </li>
                  <li class="list website mt2">
                    <label class="f5" for>
                      {{ $t('message.shared.website') }}
                    </label>
                    
                     <v-text-field
                      class="mt-1"
                      outlined
                      v-model="profile.website"
                    >
                    </v-text-field>
                  </li>
                  <li class="list organisation mt2">
                    <label class="f5" for>
                      {{ $t('message.profileEdit.organisation') }}
                    </label>
                    
                    <v-text-field
                      class="mt-1"
                      outlined
                      v-model="profile.organisation"
                    >
                    </v-text-field>
                  </li>
                </ul>

                <ul class="list mt0 pt0 pa0">
                  <li class="list twitter">
                    <label class="f5" for>
                      {{ $t('message.shared.twitter') }}
                    </label>
                    <input class="w-100 mt1" v-model="profile.twitter" />
                  </li>
                  <li class="list facebook mt2">
                    <label class="f5" for>
                      {{ $t('message.shared.facebook') }}
                    </label>
                     <v-text-field
                      class="mt-1"
                      outlined
                      v-model="profile.facebook"
                    >
                    </v-text-field>
                  </li>
                  <li class="list linkedin mt2">
                    <label class="f5" for>
                      {{ $t('message.shared.linkedIn') }}
                      <span class="f6 lh-copy i gray">
                        {{ $t('message.profileEdit.linkedInMessage') }}</span
                      >
                    </label>
                    <v-text-field
                      class="mt-1"
                      outlined
                      v-model="profile.linkedin"
                    >
                    </v-text-field>
                  </li>

                  <li class="list mt2">
                    <label class="f5" for>
                      {{ $t('message.shared.about') }}
                      <span class="f6 lh-copy i gray">
                        ({{ $t('message.shared.markdownMessage') }}
                        <a href="https://daringfireball.net/projects/markdown/"
                          >markdown</a
                        >)
                      </span>
                    </label>
                    <v-textarea
                      outlined
                      :placeholder="$t('message.shared.bioPlaceholder')"
                      v-model="profile.bio"
                      name
                      id
                      auto-grow>
                      </v-textarea>
                  </li>
                </ul>
              </div>

              <div class="cf pt2 bg-white mb4 mb5">
                <label class="typo__label">{{
                  $t('message.profileEdit.clusters')
                }}</label>
                <p class="f6 mb3">
                  <span class="f6 lh-copy i gray">{{
                    $t('message.profileEdit.clusterMessage')
                  }}</span>
                </p>
                
                <profile-clusters-component></profile-clusters-component>
              </div>

              <div class="cf pt2 bg-white mb4 mb5">
                <label class="typo__label">{{
                  $t('message.shared.tags')
                }}</label>
                <p class="f6 mb3">
                  <span class="f6 lh-copy i gray">{{
                    $t('message.shared.tagMessage')
                  }}</span>
                </p>
                <profile-tags-component></profile-tags-component>
              </div>
            </div>

            <v-btn
              class="mr-4"
              color="secondary"
              outlined
              @click="cancelFormUpdate"
            >
              {{ $t('message.shared.cancel') }}
            </v-btn>

            <v-btn
              color="primary"
              @click="onSubmit"
            >
            {{ $t('message.shared.save') }}
    </v-btn>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable */
import NavHeaderEdit from '../shared/NavHeaderEdit.vue'
import ProfileTagsComponent from '@/components/profile/ProfileTagsComponent.vue'
import ProfileClustersComponent from '@/components/profile/ProfileClusters.vue'

import { includes } from 'lodash'
import debugLib from 'debug'
import { hasPhoto } from '@/utils'

const debug = debugLib('cl8.ProfileEdit')

export default {
  name: 'ProfileEdit',
  components: {
    NavHeaderEdit,
    ProfileTagsComponent,
    ProfileClustersComponent,
  },

  data() {
    return {
      localPhoto: null
    }
  },
  computed: {
    user() {
      return this.$store.getters.currentUser
        ? this.$store.getters.currentUser
        : false
    },
    profile() {
      return this.$store.getters.profile
    },
    profileTags: function () {
      return this.profile.tags
    },
    fullTagList: function () {
      return this.$store.getters.tagList
    },
    profileClusters: function () {
      return this.profile.clusters
    },
    fullClusterList: function () {
      return this.$store.getters.fullClusterList
    }
  },
  async created() {
    debug('fetching latest profiles and tags')
    try {
      await this.$store.dispatch('fetchProfileList')
      await this.$store.dispatch('fetchTags')
      await this.$store.dispatch('fetchClusters')
    } catch (e) {
      debug("couldn't load tags or clusters for the profile: ", e)
    }
  },
  methods: {
    updatePhoto(ev) {
      debug('image added')
      // assign the photo
      debug(ev.target.files)
      if (ev.target.files.length === 1) {
        let newPhoto = ev.target.files[0]
        this.localPhoto = window.URL.createObjectURL(newPhoto)
        let payload = { profile: this.profile, photo: newPhoto }
        this.$store.dispatch('updateProfilePhoto', payload)
      }
    },
    hasPhoto,
    showPhoto(size) {
      return this.profile.photo
    },
    cancelFormUpdate() {
      debug('cancel update', this.profile)
      this.$router.push({
        name: 'viewProfile',
        params: { profileId: this.profile.id }
      })
    },
    onSubmit: function(item) {
      debug('updating profile', this.profile)
      this.$store.dispatch('updateProfile', this.profile)
    },
    setUserProfile() {
      debug('setting own profile for ', this.user)
      let user = this.user
      let matchingProfiles = this.items.filter(function (peep) {
        return peep.id === user.uid
      })
      if (matchingProfiles.length > 0) {
        debug('We have a match!', matchingProfiles[0])
        this.$store.commit('SET_PROFILE', matchingProfiles[0])
      } else {
        debug('No matches', matchingProfiles)
      }
    }
  }
}
</script>
