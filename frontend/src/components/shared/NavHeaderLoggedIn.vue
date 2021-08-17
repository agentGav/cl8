<template>
  <div v-if="loggedIn">
    <v-menu offset-y>
      <template v-slot:activator="{ on, attrs }">
        <v-btn color="primary" v-bind="attrs" v-on="on">
          <v-icon aria-label="Navigation" role="img" aria-hidden="false">
            {{ icons.mdiMenu }}
          </v-icon>
        </v-btn>
      </template>
      <v-list>
        <v-list-item @click="addUser" v-if="canAddUsers">
          {{ $t("message.shared.addUser") }}
        </v-list-item>

        <v-list-item @click="myProfile">
          {{ $t("message.navHeaderLoggedIn.myProfile") }}
        </v-list-item>
        <v-list-item @click="logout">
          {{ $t("message.navHeaderLoggedIn.logOut") }}
        </v-list-item>
      </v-list>
    </v-menu>
  </div>
</template>

<script>
import debugLib from "debug";
import { mdiMenu } from "@mdi/js";

const debug = debugLib("cl8.NavHeaderLoggedIn.vue");
export default {
  name: "Header",
  data() {
    return {
      icons: {
        mdiMenu,
      },
    };
  },
  computed: {
    canAddUsers() {
      return this.$store.getters.isAdmin;
    },
    loggedIn() {
      return this.$store.getters.currentUser;
    },
  },
  methods: {
    addUser() {
      this.$router.push({ name: "addUser" });
    },
    logout: async function() {
      debug('log out')
      await this.$store.dispatch('logout')
    },
    myProfile: function () {
      debug("setting profile back to user");
      const currentUserId = this.$store.getters.currentUser.id;
      this.$router.push({
        name: "viewProfile",
        params: { profileId: currentUserId },
      });
    },
  },
};
</script>
