<template>
  <div>
    <router-link
      v-if="canAddUsers"
      :to="{ name: 'addUser' }"
      role="link"
      tabindex="0"
      class="link dark-gray f6 nowrap f6-ns dib fr fn-ns pointer pt0 pb3 pa2-m pa2-l ph3 v-mid order-1 tr"
      >{{ $t('message.shared.addUser') }}</router-link
    >
    <span
      :title="$t('message.navHeaderLoggedIn.myProfile')"
      role="link"
      tabindex="0"
      class="link dark-gray f6 nowrap f6-ns dib fr fn-ns pointer pt0 pb3 pa2-m pa2-l ph3 v-mid order-1 tr"
      @click="myProfile"
      >{{ $t('message.navHeaderLoggedIn.myProfile') }}</span
    >
    <span
      :title="$t('message.navHeaderLoggedIn.logOut')"
      role="link"
      tabindex="0"
      class="link dark-gray f6 nowrap f6-ns dib fr fn-ns pointer pt0 pb3 pa2-m pa2-l ph3 v-mid order-1 tr"
      @click="logout"
      >{{ $t('message.navHeaderLoggedIn.logOut') }}</span
    >
  </div>
</template>

<script>
import debugLib from 'debug'
const debug = debugLib('cl8.NavHeaderLoggedIn.vue')
export default {
  name: 'Header',
  computed: {
    canAddUsers() {
      return this.$store.getters.isAdmin
    }
  },
  methods: {
    logout: function () {
      debug('log out')
      this.$store.dispatch('logout')
    },
    myProfile: function () {
      debug('setting profile back to user')
      const currentUserId = this.$store.getters.currentUser.id
      this.$router.push({
        name: 'viewProfile',
        params: { profileId: currentUserId }
      })
    }
  }
}
</script>
