var COTACOL_HIGHLIGHT_COLOR = '#ff5722';

document.body.style.setProperty('--q-color-primary', COTACOL_HIGHLIGHT_COLOR);

var EventHub = new Vue();

var Cotacol = {
  api: {
    request: function (method, url, data) {
      return axios({
        method: method,
        url: url,
        data: data
      });
    },
    getClimbs: function () {
      return this.request('get', '/api/v1/climbs/');
    },
    getClimb: function (climbId) {
      return this.request('get', '/api/v1/climbs/' + climbId + '/');
    },
    getUser: function () {
      return this.request('get', '/api/v1/user/');
    },
    updateUser: function (user) {
      return this.request('put', '/api/v1/user/', user);
    }
  },
  map: {
    climb: function (obj) {
      obj.start_point = polyline.toGeoJSON(obj.polyline).coordinates[0];
      obj.cotacol_color = (obj.cotacol_points >= 260)
        ? 'deep-orange'
        : (obj.cotacol_points < 130) ? 'grey-7' : 'dark';
      return obj;
    }
  },
  utils: {
    notifyApiError: function (error) {
      var types = {
        400: 'warning',
        401: 'warning',
        500: 'negative'
      }
      Quasar.plugins.Notify.create({
        timeout: 5000,
        type: types[error.response.status] || 'warning',
        message: error.response.data.message || null,
        caption:
          [error.response.status, ' ', error.response.statusText]
            .join('')
            .toUpperCase() || null,
        icon: null
      })
    }
  }
};

var windowMixin = {
  data: function () {
    return {
      g: {
        visibleDrawer: false,
        user: null,
      }
    };
  }
};
