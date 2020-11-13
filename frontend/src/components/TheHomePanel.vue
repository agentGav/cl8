<template>
  <div>
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
  methods: {},
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


<style media="screen" lang="scss">
p span.list {
  display: inline-block;
}

.tag-list span {
  cursor: pointer;
}

.tag-list span i.remove_icon:after {
  content: '\D7';
  color: white;
}

.tag-list span i.remove_icon {
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 1em;
  font-style: normal;
}

button.remove-tag {
  background-image: url(../assets/cross-mark.svg);
  background-size: 0.75em;
  background-repeat: no-repeat;
  background-position: top 0.5em right 0.5em;
  padding-right: 1.5em;
}
</style>
