<template>
  <div>
    <v-row>
      <v-container fluid>
        <v-row>
          <v-col>
            <v-card elevation="1">
              <v-card-actions> </v-card-actions>
              <v-form>
                <v-col class="py-0 my-0">
                  <!-- // placeholder="Search across tags, names and profile details" -->
                  <v-text-field
                    outlined
                    :placeholder="$t('message.navHeaderLoggedIn.search')"
                    name="search-term"
                    clearable
                    @input="updateSearchTerm"
                  ></v-text-field>
                  <v-fade-transition>
                    <div class="tag-list" v-if="activeTags.length > 0">
                      <p>
                        <span class="pr-2">Tags:</span>
                        <v-chip
                          color="primary"
                          v-for="tag in activeTags"
                          :key="tag"
                          :data-name="tag"
                          close
                          @click.stop.prevent="toggleTag"
                          >{{ tag }}
                        </v-chip>
                      </p>
                    </div>
                  </v-fade-transition>
                  <v-fade-transition>
                    <div class="tag-list" v-if="activeClusters.length > 0">
                      <p>
                        <span class="pr-2">Clusters:</span>
                        <v-chip
                          color="primary"
                          v-for="cluster in activeClusters"
                          :key="cluster"
                          :data-name="cluster"
                          @click.stop.prevent="toggleCluster"
                          close
                          >{{ cluster }}
                        </v-chip>
                      </p>
                    </div>
                  </v-fade-transition>

                  <v-card-actions>
                    <v-btn color="red" text small> Clear </v-btn>
                  </v-card-actions>
                </v-col>
              </v-form>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
    </v-row>
    <v-row>
      <v-col cols="12" sm="8" order="2" >

        <profile-detail v-if="profile"></profile-detail>
        <v-card elevation="1" v-else class="pa-4 intro-card">
          <h1>Welcome to constellate</h1>
          <p>Constellate is shared directory for members of this constellation. You can use it to find other members with complementary skills and interests for your projects, or just understand who else is here.</p>
        
          <h2>How to use constellate</h2>
          <p>You can type anything above to see an updated list of profiles matching your search terms, browse using tags, or both.</p>
        
          
          <h3>(Sample tags here)</h3>
          
          
        </v-card>
      </v-col>
      <v-col cols="12" sm="4" :class="profileListClassObject">
        <v-card elevation="1">
          <div class="scrollable-height">
            <the-profile-list />
          </div>
        </v-card>
      </v-col>
    </v-row>
    <div></div>
  </div>
</template>

<script>
/* eslint-disable */
import ProfileDetail from "@/components/profile/ProfileDetail.vue";
import ProfileSearchItem from "@/components/profile/ProfileSearchItem.vue";
import TheProfileList from "@/components/TheProfileList.vue";
import TheFooter from "@/components/TheFooter.vue";

import store from "@/store";
import debugLib from "debug";
const debug = debugLib("cl8.TheHomePanel");

import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);
const VueStore = new Vuex.Store(store);

export default {
  name: "TheHomePanel",
  components: {
    ProfileDetail,
    TheProfileList,
    TheFooter,
  },

  data() {
    return {
      showingProfile: false,
    };
  },
  computed: {
    profile() {
      return this.$store.getters.profile;
    },
    profileDetailClassObject: function () {
      // if there is no profile,
      // screens larger than a phone
      return {
        "d-sm-block": this.profile,
        "d-none d-sm-block": !this.showingProfile,
      };
    },
    profileListClassObject: function () {
      // only show the full profile list on
      // screens larger than a phone
      return {
        "d-block": !this.profile,
        "d-none d-sm-block": this.profile,
      };
    },
    term() {
      return this.$store.getters.currentTerm;
    },
    activeTags() {
      return this.$store.getters.activeTags;
    },
    activeClusters() {
      return this.$store.getters.activeClusters;
    },
  },
  watch: {},
  methods: {
    toggleTag: function (ev) {
      const tag = ev.target.textContent.trim();
      debug("toggleTag", { tag });
      this.$store.dispatch("updateActiveTags", tag);
    },
    toggleCluster: function (ev) {
      const cluster = ev.target.textContent.trim();
      debug("toggleCluster", { cluster });
      this.$store.dispatch("updateActiveClusters", cluster);
    },
    updateSearchTerm(term) {
      this.$store.commit("setTerm", term);
    },
  },
  created() {
    if (this.$route.params.profileId) {
      this.showingProfile = true;
      debug({ showingProfile: this.showingProfile });
    }
  },
  async beforeRouteEnter(routeTo, routeFrom, next) {
    debug("beforeRouteEnter");
    if (routeTo.params.profileId) {
      await VueStore.dispatch("fetchProfile", { id: routeTo.params.profileId });
    }
    next();
  },
  async beforeRouteUpdate(routeTo, routeFrom, next) {
    debug("beforeRouteUpdate");
    if (routeTo.params.profileId) {
      this.showingProfile = true;
      debug({ showingProfile: this.showingProfile });
      await this.$store.dispatch("fetchProfile", { id: routeTo.params.profileId });
    }
    next();
  },
};
</script>

<style>
.intro-card {
  min-height: 20rem;
}

.scrollable-height {
  max-height: 77vh;
  overflow: auto;
}
</style>
