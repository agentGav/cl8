<template>
  <div>
    <transition name="fade" mode="out-in" appear>
      <v-container>
        <v-card>
          <v-form>
            <v-row>
              <v-col class="col-12 col-md-4">
                <div class="pa-4">
                  
                <v-img v-if="hasPhoto(profile)" :src="showPhoto()" class=""></v-img>

                <v-gravatar v-else :email="profile.email" :size="200" class="" />

                <div class="">
                  <v-switch
                    v-model="profile.visible"
                    :label="profileVisibility"
                  ></v-switch>
                </div>
                <p class="" v-if="profile.visible">
                  {{ $t("message.addUser.profileVisible") }}
                </p>
                <p class="" v-else>
                  {{ $t("message.addUser.profileHidden") }}
                </p>
                </div>
              </v-col>

              <v-col>
                
                  <!-- Warning message box -->
                <div
                  v-if="warning"
                >
                  <svg
                    class="w1"
                    data-icon="info"
                    viewBox="0 0 32 32"
                    style="fill: currentcolor"
                  >
                    <title>info icon</title>
                    <path
                      d="M16 0 A16 16 0 0 1 16 32 A16 16 0 0 1 16 0 M19 15 L13 15 L13 26 L19 26 z M16 6 A3 3 0 0 0 16 12 A3 3 0 0 0 16 6"
                    />
                  </svg>
                  <span class="lh-title ml2">{{ warning }}</span>
                </div>

                <!-- Error message box -->
                <div
                  v-if="error"
                  class="flex items-center pa3 bg-light-red mb2"
                >
                  <svg
                    class="w1"
                    data-icon="info"
                    viewBox="0 0 32 32"
                    style="fill: currentcolor"
                  >
                    <title>info icon</title>
                    <path
                      d="M16 0 A16 16 0 0 1 16 32 A16 16 0 0 1 16 0 M19 15 L13 15 L13 26 L19 26 z M16 6 A3 3 0 0 0 16 12 A3 3 0 0 0 16 6"
                    />
                  </svg>
                  <span class="lh-title ml2">{{ error }}</span>
                </div>
                
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
                    outlined
                    v-model="profile.email"
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

                <div class="mx-4">
                  <h3>{{ $t("message.profileEdit.clusters") }}</h3>
                  <p>{{ $t("message.profileEdit.clusterMessage") }}</p>

                  <profile-clusters-component></profile-clusters-component>
                </div>

                <div class="mt-4 mx-4">
                  <h3>{{ $t("message.shared.tags") }}</h3>
                  <p>{{ $t("message.shared.tagMessage") }}</p>

                  <profile-tags-component></profile-tags-component>
                </div>
              
              
              <div class="mx-4">
                
              <v-checkbox
                v-model="profile.sendInvite"
                :label="$t('message.addUser.sendInvite')">
              </v-checkbox>
      
              <v-checkbox
                v-model="profile.admin"
                :label="$t('message.addUser.isAdmin')"
              ></v-checkbox>
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
import ProfileTagsComponent from "@/components/profile/ProfileTagsComponent.vue";
import TheFooter from "@/components/TheFooter.vue";

import { includes } from "lodash";
import { hasPhoto } from "@/utils";
import debugLib from "debug";

const debug = debugLib("cl8.AddUser");

export default {
  name: "AddUser",
  components: {
    // ProfileTagsComponent,
  },
  data() {
    return {
      localPhoto: null,
      warning: null,
      error: null,
      loading: false,
      profile: {
        name: "",
        email: "",
        phone: "",
        website: "",
        twitter: "",
        facebook: "",
        linkedin: "",
        bio: "",
        visible: true,
        sendInvite: false,
        pitchable: false,
        tags: [],
        clusters: [],
      },
    };
  },
  async created() {
    debug("fetching latest profiles and tags");
    try {
      await this.$store.dispatch("fetchTags");
      await this.$store.dispatch("fetchClusters");
    } catch (e) {
      debug("couldn't load tags or clusters for the profile: ", e);
    }
  },
  computed: {
    user() {
      return this.$store.getters.currentUser ? this.$store.getters.currentUser : false;
    },
    profileTags: function () {
      return this.profile.tags;
    },
    fullTagList: function () {
      return this.$store.getters.tagList;
    },
    profileClusters: function () {
      return this.profile.clusters;
    },
    fullClusterList: function () {
      return this.$store.getters.fullClusterList;
    }
  },
  methods: {
    cancelFormUpdate() {
      this.$router.push({ name: "home" });
    },
    onSubmit: async function () {
      this.error = null;
      this.warning = null;

      if (this.profile.name.length == 0) {
        this.warning = "Please enter a name for the new user";
        return;
      }

      if (this.profile.email.length == 0) {
        this.warning = "Please enter an email address for the new user";
        return;
      }

      debug("creating profile");
      this.loading = true;
      try {
        // console.log(this.profile)
        const resp = await this.$store.dispatch("addUser", this.profile);
        // Any response is a warning as `addUser` will redirect to the new
        // profile if all goes well
        // this.warning = resp
      } catch (err) {
        debug("Error creating account", err);
        this.error = err.message;
      }
      this.loading = false;
    },
    hasPhoto,
  },
};
</script>
