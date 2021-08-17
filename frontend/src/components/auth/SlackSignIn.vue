<template>
  <div>
    <v-card width="400px" class="mt-5 mx-auto">
      <v-card-title>
        <h1 class="text-center text-h5">Welcome to the CAT directory</h1>
      </v-card-title>

      <v-card-text>
        <p>
          Follow the link below to signin using the same credentials you use to
          sign into the CAT slack.
        </p>

        <a href="/accounts/slack_openid_connect/login">
          Sign in with your climateAction.tech slack account
        </a>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import debugLib from 'debug'
const debug = debugLib('cl8.Login')

export default {
  name: 'Login',
  components: {},
  data: function() {
    return {}
  },
  methods: {}
}
</script>
