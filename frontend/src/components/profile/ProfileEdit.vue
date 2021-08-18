<template>
  <div>
    <transition name="fade" mode="out-in" appear>
      <v-container>
        <v-card>
          <v-form>
            <v-row>
              <v-col class="col-12 col-md-4">
                <div class="pa-4">
                  <router-link :to="{ name: 'editProfilePhoto' }">
                    <v-img
                      class="justify-center"
                      width="200"
                      height="200"
                      v-if="profile.detail_photo"
                      :src="profile.detail_photo"
                    ></v-img>

                    <v-gravatar
                      v-else
                      :email="profile.email"
                      :size="200"
                      class=""
                    />
                  </router-link>

                  <div class="">
                    <v-switch
                      v-model="profile.visible"
                      :label="profileVisibility"
                    ></v-switch>
                  </div>
                  <p class="" v-if="profile.visible">
                    {{ $t("message.profileEdit.profileVisible") }}
                  </p>
                  <p class="" v-else>
                    {{ $t("message.profileEdit.profileHidden") }}
                  </p>
                </div>
              </v-col>
              <v-col>
                <div class="pa-4">
                  <v-text-field
                    class="mt-1"
                    outlined
                    v-model="profile.name"
                    :hint="$t('message.profileEdit.nameMessage')"
                    :label="$t('message.profileEdit.name')"
                  ></v-text-field>
                  <v-text-field
                    class="mt-1"
                    disabled
                    outlined
                    v-model="profile.email"
                    :hint="$t('message.profileEdit.emailMessage')"
                    :label="$t('message.profileEdit.email')"
                  ></v-text-field>

                  <v-text-field
                    class="mt-1"
                    outlined
                    v-model="profile.phone"
                    :hint="$t('message.profileEdit.phoneMessage')"
                    :label="$t('message.profileEdit.phone')"
                  ></v-text-field>

                  <v-text-field
                    class="mt-1"
                    outlined
                    v-model="profile.website"
                    :hint="$t('message.addUser.websiteMessage')"
                    :label="$t('message.shared.website')"
                  ></v-text-field>

                  <v-text-field
                    class="mt-1"
                    outlined
                    v-model="profile.organisation"
                    :hint="$t('message.addUser.websiteMessage')"
                    :label="$t('message.profileEdit.organisation')"
                  ></v-text-field>

                  <v-text-field
                    class="mt-1"
                    outlined
                    v-model="profile.twitter"
                    :hint="$t('message.addUser.twitterMessage')"
                    :label="$t('message.shared.twitter')"
                  ></v-text-field>

                  <v-text-field
                    class="mt-1"
                    outlined
                    v-model="profile.facebook"
                    :hint="$t('message.addUser.facebookMessage')"
                    :label="$t('message.shared.facebook')"
                  ></v-text-field>

                  <v-text-field
                    class="mt-1"
                    outlined
                    v-model="profile.linkedIn"
                    :hint="$t('message.addUser.linkedInMessage')"
                    :label="$t('message.shared.linkedIn')"
                  ></v-text-field>

                  <v-textarea
                    outlined
                    :label="$t('message.shared.about')"
                    :placeholder="$t('message.shared.bioPlaceholder')"
                    v-model="profile.bio"
                    name
                    id
                    auto-grow
                  ></v-textarea>
                </div>


                <div class="mt-4 mx-4">
                  <h3>{{ $t("message.shared.tags") }}</h3>
                  <p>{{ $t("message.shared.tagMessage") }}</p>

                  <profile-tags-component></profile-tags-component>
                </div>

                <v-divider class="mt-8 mr-8"></v-divider>

                <v-card-actions class="pt-8">
                  <v-btn
                    class="mr-4"
                    color="secondary"
                    outlined
                    @click="cancelFormUpdate"
                  >
                    {{ $t("message.shared.cancel") }}
                  </v-btn>

                  <v-btn color="primary" @click="onSubmit">
                    {{ $t("message.shared.save") }}
                  </v-btn>
                </v-card-actions>
              </v-col>
            </v-row>
          </v-form>
        </v-card>
      </v-container>
    </transition>
  </div>
</template>

<script>
/* eslint-disable */
import NavHeaderEdit from "../shared/NavHeaderEdit.vue";
import ProfileTagsComponent from "@/components/profile/ProfileTagsComponent.vue";
import ProfileClustersComponent from "@/components/profile/ProfileClusters.vue";

import Vue from "vue";
import Vuex from "vuex";
import { includes } from "lodash";
import debugLib from "debug";

import { fetchCurrentUser, hasPhoto } from "@/utils";
import store from "@/store";

const debug = debugLib("cl8.ProfileEdit");
Vue.use(Vuex);
const VueStore = new Vuex.Store(store);

export default {
  name: "ProfileEdit",
  components: {
    NavHeaderEdit,
    ProfileTagsComponent,
    ProfileClustersComponent,
  },

  data() {
    return {
      localPhoto: null,
      profileVisibility: "Show your profile",
    };
  },
  computed: {
    user() {
      return this.$store.getters.currentUser ? this.$store.getters.currentUser : false;
    },
    profile() {
      return this.$store.getters.profile;
    },
    profileTags: function () {
      return this.profile.tags;
    },
    fullTagList: function () {
      return this.$store.getters.fullTagList;
    },
    profileClusters: function () {
      return this.profile.clusters;
    },
    fullClusterList: function () {
      return this.$store.getters.fullClusterList;
    },
  },
  async beforeRouteEnter(routeTo, routeFrom, next) {
    debug("beforeRouteEnter");
    try {
      const currentUser = await fetchCurrentUser(VueStore);
      debug({ currentUser });
      await VueStore.dispatch("fetchProfile", { id: currentUser.id });
      await VueStore.dispatch("fetchTags");
      await VueStore.dispatch("fetchClusters");
    } catch (error) {
      debug("Error fetching current user", error);
    }
    next();
  },
  methods: {
    updatePhoto(ev) {
      debug("image added");
      // assign the photo
      debug(ev.target.files);
      if (ev.target.files.length === 1) {
        let newPhoto = ev.target.files[0];
        this.localPhoto = window.URL.createObjectURL(newPhoto);
        let payload = { profile: this.profile, photo: newPhoto };
        this.$store.dispatch("updateProfilePhoto", payload);
      }
    },
    hasPhoto,
    showPhoto(size) {
      return this.profile.detail_photo;
    },
    cancelFormUpdate() {
      debug("cancel update", this.profile);
      this.$router.push({
        name: "viewProfile",
        params: { profileId: this.profile.id },
      });
    },
    onSubmit: function (item) {
      debug("updating profile", this.profile);
      this.$store.dispatch("updateProfile", this.profile);
    },
    setUserProfile() {
      debug("setting own profile for ", this.user);
      let user = this.user;
      let matchingProfiles = this.items.filter(function (peep) {
        return peep.id === user.uid;
      });
      if (matchingProfiles.length > 0) {
        debug("We have a match!", matchingProfiles[0]);
        this.$store.commit("SET_PROFILE", matchingProfiles[0]);
      } else {
        debug("No matches", matchingProfiles);
      }
    },
  },
};
</script>
