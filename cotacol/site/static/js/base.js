var COTACOL_HIGHLIGHT_COLOR = '#ff5722';
var COTACOL_API_BASE_URL = 'https://api.cotacol.cc';

document.body.style.setProperty('--q-color-primary', COTACOL_HIGHLIGHT_COLOR);

var EventHub = new Vue();

var Cotacol = {
  api: {
    request: function (method, url, data, headers) {
      return axios({
        method: method,
        url: COTACOL_API_BASE_URL + url,
        data: data,
        headers: headers
      });
    },
    getClimbs: function () {
      return this.request('get', '/v1/climbs/');
    },
    getClimb: function (climbId) {
      return this.request('get', '/v1/climbs/' + climbId + '/');
    },
    getUser: function (jwt) {
      if (!jwt) return;
      return this.request('get', '/v1/users/me/', null, {
        'Authorization': 'Bearer ' + jwt.access_token
      });
    },
    updateUser: function (data, jwt) {
      if (!jwt) return;
      return this.request('patch', '/v1/users/me/', data, {
        'Authorization': 'Bearer ' + jwt.access_token
      });
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
