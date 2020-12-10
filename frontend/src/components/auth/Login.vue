<template>
  <div>
    <v-card width="400px" class="mt-5 mx-auto">
      <v-card-title>
        <h1 class="text-center text-h5">Welcome to the constellation</h1>
      </v-card-title>

      <v-alert
        v-if="announcement"
        text
        color="warning"
        dismissible
        transition="fade-transition"
        v-model="announcementAlert"
      >
        <p v-for="(errors, key) in announcement" :errors="errors" :key="key">
          {{ key }}:
          <span v-for="(error, index) in errors" :key="index">
            {{ error }}
          </span>
        </p>
      </v-alert>

      <v-card-text>
        <p>
          {{ $t("message.login.instructions") }}
        </p>
        <v-form v-on:submit.prevent lazy-validation ref="form" v-model="formIsValid">
          <v-text-field
            label="your email address"
            v-model="email"
            :rules="[rules.required, rules.email]"
          ></v-text-field>

          <v-card-actions>
            <v-btn
              :loading="this.submissionInFlight"
              :disabled="!formIsValid"
              color="info"
              @click="submitEmail"
              >Request login code</v-btn
            >
          </v-card-actions>
        </v-form>
      </v-card-text>

      <div v-if="emailSubmitted">
        <v-form v-on:submit.prevent>
          <v-card-text>
            <p class="gray measure tl lh-copy next-step-guidance">
              {{ $t("message.login.emailSubmitted.nextStepGuidance") }}
            </p>

            <v-text-field
              data-name="login-code"
              v-model="token"
              label="login code"
              :placeholder="$t('message.login.emailSubmitted.loginCode')"
            />
          </v-card-text>

          <v-card-actions>
            <v-btn data-name="sign-in" @click="signIn">
              {{ $t("message.login.emailSubmitted.signinButton") }}
            </v-btn>
            <v-btn name="button" @click="resetForm">
              {{ $t("message.login.emailSubmitted.resetButton") }}
            </v-btn>
          </v-card-actions>
        </v-form>
      </div>

      <v-card-text>
        <p class="text-caption">
          <em>
            {{ $t("message.login.helpInstructions.question") }}

            <a class="" :href="supportEmail">
              {{ $t("message.login.helpInstructions.suggestion") }} </a
            >.
          </em>
        </p>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import debugLib from "debug";
const debug = debugLib("cl8.Login");

export default {
  name: "Login",
  components: {},
  data: function () {
    return {
      rules: {
        required: (value) => !!value || "Email is required",
        email: (value) => {
          const pattern = /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
          return pattern.test(value) || "Invalid e-mail.";
        },
      },
      email: "",
      token: null,
      announcement: "",
      announcementAlert: false,
      formIsValid: false,
      emailSubmitted: false,
      submissionInFlight: false,
      supportEmail: `mailto:${process.env.VUE_APP_SUPPORT_EMAIL}`,
    };
  },
  methods: {
    resetForm: function () {
      this.email = null;
      this.emailSubmitted = false;
      this.submissionInFlight = false;
      this.loginInFLight = false;
    },
    signIn: function () {
      let user = {
        email: this.email,
        token: this.token,
      };
      this.$store.dispatch("login", user);
    },
    submitEmail: async function () {
      this.submissionInFlight = true;
      let emailSubmitted;
      debug("Submitting", this.email);
      try {
        emailSubmitted = await this.$store.dispatch("submitEmail", this.email);
      } catch (e) {
        // bubble up the error so we see it in the login
        debug("Oops. Exception reported", { e });

        // the server crashed serving this request
        if (e.response.status == 500) {
          debug("Error from the server", { e });
          this.announcement = {
            non_field_errors: [
              "Sorry, we had a problem connecting to the server. Please try again later.",
            ],
          };
          // set the v-model on the alert, in case it was dismissed
          // before
          this.announcementAlert = true;
        }
        // the servers up, but didn't like the
        // paylaod we sent and is telling us what it
        // didn't like
        if (e.response.status == 400) {
          let errors = e.response.data;
          this.announcement = errors;
          this.announcementAlert = true;
        }
      }

      this.submissionInFlight = false;
      if (emailSubmitted) {
        this.emailSubmitted = true;
      }
    },
    validate() {
      this.$refs.form.validate();
    },
  },
  computed: {
    signInData: function () {
      return this.$store.getters.signInData;
    },
  },
};
</script>
