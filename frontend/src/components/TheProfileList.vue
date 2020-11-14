<template>
  <div>
    <div class="tag-list" v-if="activeTags.length > 0">
      <p>
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

    <div class="tag-list" v-if="activeClusters.length > 0">
      <p>
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

    <ul class="list">
      <profile-search-item
        v-for="item in searchResults"
        :item="item"
        :key="item.id"
      />
    </ul>
  </div>
</template>

<script>
import { includes } from 'lodash'

import ProfileSearchItem from '@/components/profile/ProfileSearchItem.vue'
import debugLib from 'debug'
const debug = debugLib('cl8.TheProfileList')

const searchKeys = ['name', 'email', 'tags.name']
const searchOptions = {
  keys: searchKeys,
  defaultAll: true,
  threshold: 0.2
}

export default {
  name: 'TheProfileList',
  components: {
    ProfileSearchItem
  },
  data() {
    return {
      loading: true,
      searchResults: []
    }
  },
  computed: {
    term() {
      return this.$store.getters.currentTerm
    },
    activeTags() {
      return this.$store.getters.activeTags
    },
    activeClusters() {
      return this.$store.getters.activeClusters
    },
    profileList() {
      return this.$store.getters.profileList
    }
  },
  watch: {
    term() {
      this.checkAgainstSearch()
    },
    activeTags() {
      this.checkAgainstSearch()
    },
    activeClusters() {
      this.checkAgainstSearch()
    }
  },
  async created() {
    debug('created')
    this.$store.commit('startLoading')

    // make a new promise to fetch this stuff, then after they have loaded show the stuff
    try {
      await this.$store.dispatch('fetchProfileList')
      debug('loaded the profiles in the component')
      this.searchResults = this.profileList
      this.$store.commit('stopLoading')
      this.loading = false
    } catch (e) {
      debug("couldn't load in the profile: ", e)
    }
  },

  methods: {
    checkAgainstSearch() {
      debug('checkAgainstSearch: filtering against matching tags:', this.term)
      let searchResults = this.matchingTags()
      this.searchResults = this.matchingClusters(searchResults)

      debug('this.searchResults', this.searchResults.length)

      // if we have a term to search against too, after ouer tags
      if (this.term !== '') {
        debug('checkAgainstSearch: searching against term:', this.term)
        this.$search(this.term, this.searchResults, searchOptions).then(
          (results) => {
            debug('checkAgainstSearch: results', results.length)
            this.searchResults = results
          }
        )
      }
    },
    toggleTag: function (ev) {
      const tag = ev.target.textContent.trim()
      debug('toggleTag', { tag })
      this.$store.dispatch('updateActiveTags', tag)
    },
    toggleCluster: function (ev) {
      const cluster = ev.target.textContent.trim()
      debug('toggleCluster', { cluster })
      this.$store.dispatch('updateActiveClusters', cluster)
    },
    matchingClusters(profileList) {
      const clusters = this.activeClusters
      if (typeof clusters === 'undefined' || clusters === '') {
        return profileList
      }
      clusters.forEach(function (cluster) {
        profileList = profileList.filter(function (profile) {
          const profileClusters = profile.clusters.map(function (clst) {
            return clst.name.toLowerCase()
          })
          return includes(profileClusters, cluster)
        })
      })
      return profileList
    },
    matchingTags() {
      const activeTags = this.activeTags
      const activeClusters = this.activeClusters
      debug('matchingTags', { activeTags }, { activeClusters })

      const noActiveTags =
        typeof activeTags === 'undefined' || activeTags === ''
      const noActiveClusters =
        typeof activeClusters === 'undefined' || activeClusters === ''

      if (noActiveTags && noActiveClusters) {
        debug('returning early. no clusters or tags to filter by')
        return this.profileList
      }

      const availableProfiles = this.profileList
      let profilesFilteredByTags

      debug('availableProfiles', { availableProfiles })
      // clear out profiles with NO tags
      if (!noActiveTags) {
        // now reduce the list till we only have people matching all tags
        activeTags.forEach(function (activeTag) {
          profilesFilteredByTags = availableProfiles.filter(function (profile) {
            const profileTags = profile.tags.map(function (tag) {
              return tag.name.toLowerCase()
            })
            debug('comparing', { profileTags }, { activeTag })
            return includes(profileTags, activeTag)
          })
        })
      }
      debug('profilesFilteredByTags', { profilesFilteredByTags })
      let profilesFilteredByClusters =
        profilesFilteredByTags || availableProfiles
      if (!noActiveClusters) {
        debug('checking against matchingClusters', activeClusters)
        activeClusters.forEach(function (clusterName) {
          profilesFilteredByClusters = profilesFilteredByClusters.filter(
            function (profile) {
              const profileClusters = profile.clusters.map(function (cluster) {
                return cluster.name.toLowerCase()
              })
              debug('comparing', { profileClusters }, { clusterName })
              return includes(profileClusters, clusterName)
            }
          )
        })
      }
      debug('profilesFilteredByClusters', { profilesFilteredByClusters })
      return profilesFilteredByClusters
    }
  }
}
</script>
