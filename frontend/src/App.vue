<template>
  <v-app>
    <v-navigation-drawer app v-model="drawer" absolute bottom temporary>
      <!-- -->
      <slot></slot>
    </v-navigation-drawer>

    <v-app-bar app flat>
      <!-- -->
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
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
      <div class="row">
        <div class="col pa-0 ma-0">
          <p class="text-center text-caption pa-0 ma-0">
            <em>{{ $t('message.footer.helpMessage') }}</em>
          </p>
        </div>
      </div>
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
    return {
      drawer: false
    }
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
