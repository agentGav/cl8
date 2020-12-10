<template>
  <v-app>
    <v-app-bar app flat color="white">
      <v-toolbar flat>
        <v-toolbar-title>Constellate</v-toolbar-title>
        <v-spacer></v-spacer>
        <nav-header-logged-in></nav-header-logged-in>
      </v-toolbar>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <transition>
          <router-view></router-view>
        </transition>
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
import NavHeaderLoggedIn from '@/components/shared/NavHeaderLoggedIn.vue'
// eslint-disable-next-line
const debug = debugLib('cl8.App')

export default {
  components: {
    NavHeaderLoggedIn
  },
  name: 'app',
  data() {
    return {
      drawer: false
    }
  },
  computed: {
    loggedIn() {
      return this.$store.getters.profile
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
