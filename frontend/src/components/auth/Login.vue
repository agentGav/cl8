<template>
  <div>
    <v-card width="400px" class="mt-5 mx-auto">
      <!-- checkign for email -->

      <v-card-title>
        <h1 class="text-center text-h5">Welcome to the constellation</h1>
      </v-card-title>
      <v-card-text>
        <p>
          {{ $t('message.login.instructions') }}
        </p>
        <v-form v-on:submit.prevent>
          <v-text-field label="your email address" v-model="email" />

          <v-card-actions>
            <v-btn class="" color="info" @click="submitEmail"
              >Request login code</v-btn
            >
          </v-card-actions>
        </v-form>
      </v-card-text>

      <div v-if="emailSubmitted">
        <v-form v-on:submit.prevent>
          <v-card-text>
            <p class="gray measure tl lh-copy next-step-guidance">
              {{ $t('message.login.emailSubmitted.nextStepGuidance') }}
            </p>

            <v-text-field v-model="token" label="token" />
          </v-card-text>

          <v-card-actions>
            <v-btn @click="signIn">
              {{ $t('message.login.emailSubmitted.signinButton') }}
            </v-btn>
            <v-btn name="button" @click="resetForm">
              {{ $t('message.login.emailSubmitted.resetButton') }}
            </v-btn>
          </v-card-actions>
        </v-form>
      </div>

      <v-card-text>
        <p class="text-caption">
          <em>
            {{ $t('message.login.helpInstructions.question') }}

            <a class="" :href="supportEmail">
              {{ $t('message.login.helpInstructions.suggestion') }} </a
            >.
          </em>
        </p>
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
  data: function () {
    return {
      email: '',
      token: null,
      announcement: '',
      formIsValid: false,
      emailSubmitted: false,
      supportEmail: `mailto:${process.env.VUE_APP_SUPPORT_EMAIL}`
    }
  },
  methods: {
    checkForValidFormSubmission: function () {
      let validation = {
        email: this.email
      }

      return this.$validator
        .validateAll(validation)
        .then((result) => {
          if (!result) {
            this.formIsValid = result
            return false
          }
          this.formIsValid = result
          return result
        })
        .catch((err) => {
          debug(err)
        })
    },
    resetForm: function () {
      this.email = null
      this.emailSubmitted = false
    },
    signIn: function () {
      let user = {
        email: this.email,
        token: this.token
      }
      this.$store.dispatch('login', user)
    },
    submitEmail: async function () {
      // TODO set loading state with viewtify

      let emailSubmitted
      try {
        emailSubmitted = await this.$store.dispatch('submitEmail', this.email)
      } catch (e) {
        debug({ e })
        // bubble up the error so we see it in the login
      }

      if (emailSubmitted) {
        this.emailSubmitted = true
      }
    }
  },
  computed: {
    formValid: function () {
      return this.formIsValid
    },
    signInData: function () {
      return this.$store.getters.signInData
    },
    loading: function () {
      return this.$store.getters.isLoading
    }
  }
}
</script>

<style>


input {
  outline-style: none;
}

.sign-in-prompt {
  margin-left: auto;
  margin-right: auto;
  background-repeat: no-repeat;
}

.sign-in-prompt a {
  top: 175px;
  left: 145px;
}

.vh {
  position: absolute !important;
  clip: rect(1px, 1px, 1px, 1px);
  padding: 0 !important;
  border: 0 !important;
  height: 1px !important;
  width: 1px !important;
  overflow: hidden;
}

.spinner {
  position: absolute;
  display: flex;
  justify-content: center;
  height: 100vh;
  width: 100vw;
  background-color: white;
  top: 0;
  bottom: 0;
  left: 0;
  right: 0;
}
</style>
