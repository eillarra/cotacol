Vue.component('cotacol-climb-points', {
  props: {
    climb: {
      type: [Object],
      required: true
    },
    size: {
      type: [String],
      default: '40px'
    },
    showValue: {
      type: [Boolean],
      default: true
    }
  },
  template: `
    <q-circular-progress
      :max="363"
      :value="climb.cotacol_points"
      :show-value="showValue"
      :size="size"
      :thickness="0.25"
      :color="climb.cotacol_color"
      track-color="grey-3"
    ></q-circular-progress>
  `
});

var Store = new Vuex.Store({
  state: {
    user: null,
    climbs: [],
    filter: 'all'
  },
  getters: {
    filteredClimbs: function (state) {
      var f = state.filter;
      var u = state.user;

      if (f == 'all' || !u) return state.climbs;

      return Object.freeze(state.climbs.slice().filter(function (obj) {
        return u.extra_data[f].indexOf(obj.id) > -1;
      }));
    }
  },
  mutations: {
    fetchUser: function (state) {
      Cotacol.api.getUser().then(function (res) {
        if (res.data.extra_data == null) res.data.extra_data = {};
        if (!_.has(res.data.extra_data, "bookmarks")) res.data.extra_data.bookmarks = [];
        if (!_.has(res.data.extra_data, "climbed")) res.data.extra_data.climbed = [];
        state.user = res.data;
      }).catch(function (err) {
        state.user = null;
      });
    },
    fetchClimbs: function (state) {
      Cotacol.api.getClimbs().then(function (res) {
        state.climbs = Object.freeze(res.data.map(function (obj) {
          return Cotacol.map.climb(obj);
        }));
      });
    },
    filterClimbs: function (state, filter) {
      state.filter = filter;
    }
  }
});

var UpdateUserListMixin = {
  methods: {
    updateUserList: function (userList, climbId) {
      var idx = this.user.extra_data[userList].indexOf(climbId);

      if (idx > -1) {
        this.user.extra_data[userList].splice(idx, 1);
      } else {
        this.user.extra_data[userList].push(climbId);
      }
      Cotacol.api.updateUser(this.user);
    }
  }
}

var ClimbListView = {
  mixins: [UpdateUserListMixin],
  template: `
    <div>
      <div class="q-pa-md">
        <div class="row q-col-gutter-xl">
          <q-select v-if="user" dense borderless v-model="filter" :options="filterOptions" label="Show" emit-value map-options class="col-6" />
          <q-select dense borderless v-model="sort" :options="sortOptions" label="Sort by" emit-value map-options class="col-6" />
        </div>
      </div>
      <q-virtual-scroll
        :items="sortedClimbs"
        :virtual-scroll-item-size="69"
        :virtual-scroll-slice-size="40"
        style="max-height: 2000px"
        separator
      >
        <template v-slot="{ item, index }">
          <q-slide-item :key="item.id" @left="onLeft(item.id)">
            <template v-slot:left>
              <div class="row items-center">
                <q-icon left name="done" /> Climbed
              </div>
            </template>
            <q-item clickable :to="{name: 'climb', params: {id: item.id}}">
              <q-item-section avatar>
                <cotacol-climb-points :climb="item"></cotacol-climb-points>
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ item.name }}</q-item-label>
                <q-item-label caption lines="2">
                  <q-icon name="straighten" size="xs" /> {{ item.distance }} m
                  <q-icon name="change_history" size="xs" /> {{ item.avg_grade }} %<br>
                  {{ item.city }}, {{ item.province }}
                </q-item-label>
              </q-item-section>
              <q-item-section side top>
                <q-item-label caption>#{{ item.id }}</q-item-label>
                <q-icon name="chevron_right" color="grey-7" />
              </q-item-section>
            </q-item>
          </q-slide-item>
        </template>
      </q-virtual-scroll>
      <div v-show="filter == 'bookmarks' && !user.extra_data.bookmarks.length" class="q-pa-xl text-center">
        <q-icon name="bookmark_border" size="xl" color="deep-orange-2" />
        <p class="text-body1 q-mt-lg">You don't have bookmarks.</p>
      </div>
      <div v-show="filter == 'climbed' && !user.extra_data.climbed.length" class="q-pa-xl text-center">
        <q-icon name="search_off" size="xl" color="deep-orange-2" />
        <p class="text-body1 q-mt-lg">Go out and ride!</p>
      </div>
    </div>
  `,
  data: function () {
    return {
      filter: 'all',
      filterOptions: Object.freeze([
        {label: 'All', value: 'all'},
        {label: 'Bookmarks', value: 'bookmarks'},
        {label: 'Climbed', value: 'climbed'},
      ]),
      sort: 'name',
      sortOptions: Object.freeze([
        {label: 'COTACOL ID', value: 'id'},
        {label: 'COTACOL points', value: 'cotacol_points'},
        {label: 'Distance', value: 'distance'},
        {label: 'Average grade', value: 'avg_grade'},
        {label: 'Name', value: 'name'}
      ])
    };
  },
  computed: _.extend(
    Vuex.mapState(['user']),
    Vuex.mapGetters(['filteredClimbs']), {
    sortedClimbs: function () {
      var s = this.sort;

      if (s == 'id') return this.filteredClimbs;

      if (["avg_grade", "distance", "cotacol_points"].indexOf(s) !== -1) {
        return Object.freeze(this.filteredClimbs.slice().sort(function (a, b) {
          return b[s] - a[s];
        }));
      }

      return Object.freeze(this.filteredClimbs.slice().sort(function (a, b) {
        var a = a.name.toLowerCase();
        var b = b.name.toLowerCase();
        if (a < b) return -1;
        if (a > b) return 1;
        return 0;
      }));
    }
  }),
  watch: {
    'filter': function (val) {
      this.$store.commit('filterClimbs', val);
    }
  }
};

var ClimbDetailView = {
  mixins: [UpdateUserListMixin],
  template: `
    <div v-if="climb" class="q-pa-md">
      <q-btn flat round :to="{name: 'climbs'}" size="sm" icon="close" class="float_right"></q-btn>
      <p v-if="user" class="float-right q-gutter-sm">
        <q-btn round unelevated @click.prevent="updateUserList('bookmarks', climb.id)" size="sm"
          :color="(inBookmarks) ? 'dark' : 'grey-5'"
          :icon="(inBookmarks) ? 'bookmark' : 'bookmark_border'">
          <q-tooltip v-if="inBookmarks">In your bookmarks</q-tooltip>
          <q-tooltip v-else>Add to bookmarks</q-tooltip>
        </q-btn>
        <q-btn round unelevated @click.prevent="updateUserList('climbed', climb.id)" size="sm"
          :color="(inClimbed) ? 'positive' : 'grey-5'"
          :icon="(inClimbed) ? 'check' : 'add'">
          <q-tooltip v-if="inClimbed">You have climbed this one!</q-tooltip>
          <q-tooltip v-else>Add to climbed</q-tooltip>
        </q-btn>
      </p>
      <q-separator class="q-my-md" />
      <h5 class="q-mb-none">{{ climb.name }}</h5>
      <p class="text-caption q-mt-none q-mb-lg">{{ climb.city }}, {{ climb.province }}</p>
      <q-list dense>
        <q-item>
          <q-item-section avatar>
            <cotacol-climb-points :climb="climb" size="24px" :show-value="false"></cotacol-climb-points>
          </q-item-section>
          <q-item-section>COTACOL points</q-item-section>
          <q-item-section side>
            <q-item-label><strong>{{ climb.cotacol_points }}</strong></q-item-label>
          </q-item-section>
        </q-item>
        <q-separator spaced inset="item" />
        <q-item>
          <q-item-section avatar>
            <q-icon color="dark" name="straighten" />
          </q-item-section>
          <q-item-section>Distance</q-item-section>
          <q-item-section side>
            <q-item-label><strong>{{ climb.distance }} m</strong></q-item-label>
          </q-item-section>
        </q-item>
        <q-separator spaced inset="item" />
        <q-item>
          <q-item-section avatar>
            <q-icon color="dark" name="change_history" />
          </q-item-section>
          <q-item-section>Avg. grade</q-item-section>
          <q-item-section side>
            <q-item-label><strong>{{ climb.avg_grade }} %</strong></q-item-label>
          </q-item-section>
        </q-item>
        <q-separator spaced inset="item" />
        <q-item>
          <q-item-section avatar>
            <q-icon color="dark" name="trending_up" />
          </q-item-section>
          <q-item-section>Elevation diff.</q-item-section>
          <q-item-section side>
            <q-item-label><strong>{{ climb.elevation_diff }} m</strong></q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </div>
  `,
  data: function () {
    return {
      climbFull: null
    };
  },
  props: ['id'],
  computed: _.extend(
    Vuex.mapState(['climbs', 'user']), {
    climb: function () {
      if (this.climbs.length == 0) return null;
      if (this.climbFull) return Object.freeze(this.climbFull);
      return Object.freeze(_.findWhere(this.climbs, {id: this.id}));
    },
    inBookmarks: function () {
      return this.user && this.climb && this.user.extra_data.bookmarks.indexOf(this.climb.id) > -1;
    },
    inClimbed: function () {
      return this.user && this.climb && this.user.extra_data.climbed.indexOf(this.climb.id) > -1;
    }
  }),
  methods: {
    goBack: function () {
      this.$router.push({name: 'climbs'});
    }
  },
  /*beforeRouteEnter: function (to, from, next) {
    var self = this;
    Cotacol.api.getClimb(this.id).then(function (res) {
      self.climbFull = Cotacol.map.climb(res.data);
    });
    next();
  }*/
};

var Router = new VueRouter({
  routes: [
    {
      name: 'climbs',
      path: '/',
      pathToRegexpOptions: {strict: true},
      component: ClimbListView
    },
    {
      name: 'climb',
      path: '/climbs/:id/',
      pathToRegexpOptions: {strict: true},
      components: {
        default: ClimbListView,
        detail: ClimbDetailView
      },
      props: {
        detail: function (route) {
          return {
            id: +route.params.id
          };
        }
      }
    }
  ]
});

new Vue({
  el: '#vue',
  mixins: [windowMixin],
  store: Store,
  router: Router,
  data: function () {
    return {
      visibleMenu: true
    };
  },
  computed: _.extend(
    Vuex.mapGetters(['filteredClimbs']), {
  }),
  methods: {
    goToClimb: function (climbId) {
      this.$router.push({name: 'climb', params: {id: climbId}});
    },
  },
  created: function () {
    this.$store.commit('fetchClimbs');
    this.$store.commit('fetchUser');
    EventHub.$on('cotacol-map-select-climb', this.goToClimb);
  },
  beforeDestroy: function () {
    EventHub.$off('cotacol-map-select-climb');
  }
});
