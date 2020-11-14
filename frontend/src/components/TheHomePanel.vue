<template>
  <div>
    <v-row>
      <v-container>
      <v-form>
        <v-col>
          <!-- // placeholder="Search across tags, names and profile details" -->
          <v-text-field
            outlined
            :placeholder="$t('message.navHeaderLoggedIn.search')"
            name="search-term"
            @input="updateSearchTerm"
          ></v-text-field>
        </v-col>
        
      </v-form>
      </v-container>
    </v-row>
    <v-row>
      <v-col order="2" v-if="profile">
        <profile-detail />
      </v-col>
      <v-col cols="4">
        <div class="">
          <the-profile-list />
        </div>
      </v-col>
    </v-row>
    <div></div>
  </div>
</template>

<script>
/* eslint-disable */
import ProfileDetail from '@/components/profile/ProfileDetail.vue'
import ProfileSearchItem from '@/components/profile/ProfileSearchItem.vue'
import TheProfileList from '@/components/TheProfileList.vue'
import TheFooter from '@/components/TheFooter.vue'

import store from '@/store'
import debugLib from 'debug'
const debug = debugLib('cl8.TheHomePanel')

import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)
const VueStore = new Vuex.Store(store)

export default {
  name: 'TheHomePanel',
  components: {
    ProfileDetail,
    TheProfileList,
    TheFooter
  },

  data() {
    return {}
  },
  computed: {
    profile() {
      return this.$store.getters.profile
    }
  },
  watch: {},
  methods: {
    updateSearchTerm(term) {
      this.$store.commit('setTerm', term)
    }
  },
  async beforeRouteEnter(routeTo, routeFrom, next)  {
        debug("beforeRouteEnter")
        if (routeTo.params.profileId) {
          await VueStore.dispatch('fetchProfile', {id: routeTo.params.profileId})
        }
        next()
  },
  async beforeRouteUpdate(routeTo, routeFrom, next)  {
        debug("beforeRouteUpdate")
        if (routeTo.params.profileId) {
          await this.$store.dispatch('fetchProfile', {id: routeTo.params.profileId})
        }
        next()
  },
}
</script>
