<template>
  <v-app>
    <v-navigation-drawer app temporary>
      <!-- -->
    </v-navigation-drawer>

    <v-app-bar app flat>
      <!-- -->
      <h1 class="text-center text-h5">Icebreaker One</h1>
    </v-app-bar>

    <!-- Sizes your content based upon application components -->
    <v-main>
      <!-- Provides the application the proper gutter -->
      <v-container fluid>
        <!-- If using vue-router -->
        <router-view></router-view>
      </v-container>
    </v-main>

    <v-footer app>
      <!-- -->
    </v-footer>
  </v-app>
</template>

<script>
import debugLib from 'debug'
import { fetchCurrentUser } from './utils'
// eslint-disable-next-line
const debug = debugLib('cl8.App')

export default {
  components: {},
  name: 'app',
  data() {
    return {}
  },
  methods: {},
  async mounted() {
    // if a user is not logged in, push to the login
    debug('mounted')
    const currentUser = await fetchCurrentUser(this.$store)

    if (!currentUser) {
      if (this.$router.currentRoute.name !== 'signin') {
        this.$router.push({ name: 'signin' })
      }
    }
  }
}
</script>

<style>
</style>
