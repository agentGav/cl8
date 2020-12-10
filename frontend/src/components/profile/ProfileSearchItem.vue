<template>
  <div>
    <v-divider v-if="index > 0"></v-divider>

    <v-list-item
      :data-atid="item.id"
      :key="item.id"
      class="profile"
      @click="profileChosen"
      tabindex="0"
    >
      <v-list-item-avatar>
        <img v-if="hasPhoto(item)" :src="showPhoto('thumbnail')" class="" />

        <v-gravatar
          v-else
          :email="item.email"
          :size="64"
          class="gravatar fl b--light-silver ba"
        />
      </v-list-item-avatar>

      <v-list-item-content>
        <v-list-item-title>
          {{ item.name }}
        </v-list-item-title>

        <v-list-item-subtitle v-if="item.organisation">
          {{ item.organisation }}
        </v-list-item-subtitle>

        <div class="dib mt1-m">
          <v-chip small class="ma-1" v-for="tag in item.tags" :key="tag.id"
            >{{ tag.name }}
          </v-chip>
        </div>
      </v-list-item-content>
    </v-list-item>
  </div>
</template>

<script>
import Vue from "vue";
import { hasPhoto } from "@/utils";
import Gravatar from "vue-gravatar";
import debugLib from "debug";
const debug = debugLib("cl8.ProfileSearchItem");
Vue.component("v-gravatar", Gravatar);

export default {
  props: {
    item: {
      type: Object,
      default: function () {
        return {
          name: "default",
          photo: null,
        };
      },
    },
    index: {
      type: Number,
      default: 0,
    },
  },
  data() {
    return {};
  },
  computed: {},
  methods: {
    profileChosen() {
      debug({ profile: this.item });
      debug({ profileId: this.item.id });
      this.$router.push({ name: "viewProfile", params: { profileId: this.item.id } });
    },
    hasPhoto,
    showPhoto(size) {
      if (size == "thumbnail") {
        return this.item.thumbnail_photo;
      } else {
        return this.item.photo;
      }
    },
  },
};
</script>

<style>
li.peep {
  cursor: pointer;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
</style>
