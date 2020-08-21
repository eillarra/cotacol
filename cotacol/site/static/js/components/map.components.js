var MAPBOX_ACCESS_TOKEN = 'pk.eyJ1IjoiZWlsbGFycmEiLCJhIjoiY2lwZ3dhN2x0MDAxanZibnR2OG02MGVoZyJ9.NUtUY72YGX4lHvNZb7wRfw';
var BE_MAX_BOUNDS = [[2, 49], [7, 51.5]];

Vue.component('cotacol-map', {
  data: function () {
    return {
      map: null,
      maxZoom: 15
    };
  },
  props: ['climbs'],
  template: `
    <div>
      <div ref="map" style="position: absolute; left: 0; top:0; bottom: 0; width: 100%"></div>
    </div>
  `,
  computed: {
    lineStrings: function () {
      if (!this.climbs || this.climbs.length == 0) return null;

      var output = {};

      _.each(this.climbs, function (obj) {
        output[obj.id] = polyline.toGeoJSON(obj.polyline);
      });

      return output;
    },
    features: function () {
      if (!this.climbs || this.climbs.length == 0) return null;

      var output = [];

      _.each(this.climbs, function (obj) {
        output.push({
          type: 'Feature',
          id: obj.id,
          geometry: {
            type: 'Point',
            coordinates: obj.start_point
          }
        });
      });

      return {
        'type': 'FeatureCollection',
        'features': output
      };
    }
  },
  methods: {
    addLayers: function () {
      var self = this;

      if (!this.climbs || this.climbs.length == 0) {
        setTimeout(function () { self.addLayers(); }, 25);
        return;
      }

      self.map.addSource('climbs', {
        type: 'geojson',
        buffer: 0,
        cluster: true,
        clusterMaxZoom: 9,
        clusterRadius: 50,
        data: self.features
      });

      self.map.addSource('selected-climb', {
        type: 'geojson',
        buffer: 0,
        data: null
      });

      self.map.addLayer({
        id: 'clusters',
        type: 'circle',
        source: 'climbs',
        filter: ['has', 'point_count'],
        paint: {
          'circle-translate': [0, -2],
          'circle-color': [
            'step',
            ['get', 'point_count'],
            '#aaa',
            25,
            '#777',
            50,
            '#444',
            100,
            '#1d1d1d'
          ],
          'circle-radius': [
            'step',
            ['get', 'point_count'],
            18,
            25,
            26,
            50,
            34,
            100,
            42
          ]
        }
      });

      self.map.addLayer({
        'id': 'selected-climb',
        'type': 'line',
        'source': 'selected-climb',
        'layout': {
          'line-join': 'round',
          'line-cap': 'round'
        },
        'paint': {
          'line-color': COTACOL_HIGHLIGHT_COLOR,
          'line-width': 4
        }
      });

      self.map.addLayer({
        id: 'cluster-count',
        type: 'symbol',
        source: 'climbs',
        filter: ['has', 'point_count'],
        layout: {
          'text-field': '{point_count_abbreviated}',
          'text-font': ['Roboto Medium', 'Arial Unicode MS Bold'],
          'text-size': 14
        },
        paint: {
          'text-color': '#ffffff'
        }
      });

      self.map.addLayer({
        id: 'unclustered-climb',
        type: 'circle',
        source: 'climbs',
        filter: ['!', ['has', 'point_count']],
        paint: {
          'circle-color': COTACOL_HIGHLIGHT_COLOR,
          'circle-radius': 6,
          'circle-stroke-width': 2,
          'circle-stroke-color': '#fff'
        }
      });

      self.map.on('click', 'clusters', function (el) {
        var features = self.map.queryRenderedFeatures(el.point, {
          layers: ['clusters']
        });

        var clusterId = features[0].properties.cluster_id;

        self.map.getSource('climbs').getClusterExpansionZoom(clusterId, function (err, zoom) {
          if (err) return;
          self.map.easeTo({
            center: features[0].geometry.coordinates,
            zoom: zoom
          });
        });
      });

      self.map.on('click', 'unclustered-climb', function (el) {
        var climbId = el.features[0].id;

        EventHub.$emit('cotacol-map-select-climb', climbId);

        if (self.map.getZoom() < 10) {
          self.map.easeTo({
            center: el.features[0].geometry.coordinates,
            zoom: 11
          });
        }

        self.map.getSource('selected-climb').setData({
          'type': 'Feature',
          'geometry': self.lineStrings[climbId]
        });
      });

      self.map.on('mouseenter', 'clusters', function () {
        self.map.getCanvas().style.cursor = 'pointer';
      });
    }
  },
  mounted: function () {
    mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN;
    var addLayers = this.addLayers;

    this.map = new mapboxgl.Map({
      container: this.$refs["map"],
      style: 'mapbox://styles/eillarra/cke2myfqg12j71an7jm0c9psv',
      center: [4.6, 50.2],
      maxZoom: this.maxZoom,
      minZoom: 7,
      zoom: 7.6,
      pitch: 35,
      maxBounds: BE_MAX_BOUNDS
    });

    this.map.on('load', function () {
      addLayers();
    });
  }
});


Vue.component('cotacol-climb-map', {
  data: function () {
    return {
      map: null
    };
  },
  props: ['climb'],
  template: `
    <div>
      <div ref="map" style="height: 250px; width: 100%" class="full-width rounded-borders"></div>
    </div>
  `,
  methods: {
    addLayers: function () {
      this.map.addSource('polyline', {
        type: 'geojson',
        buffer: 0,
        data: {
          'type': 'Feature',
          'geometry': polyline.toGeoJSON(this.climb.polyline)
        }
      });

      this.map.addLayer({
        'id': 'polyline',
        'type': 'line',
        'source': 'polyline',
        'layout': {
          'line-join': 'round',
          'line-cap': 'round'
        },
        'paint': {
          'line-color': COTACOL_HIGHLIGHT_COLOR,
          'line-width': 4
        }
      });
    }
  },
  mounted: function () {
    mapboxgl.accessToken = MAPBOX_ACCESS_TOKEN;
    var addLayers = this.addLayers;

    this.map = new mapboxgl.Map({
      container: this.$refs["map"],
      style: 'mapbox://styles/eillarra/cke2myfqg12j71an7jm0c9psv',
      center: this.climb.start_point,
      zoom: 12,
      pitch: 50,
      maxBounds: BE_MAX_BOUNDS
    });

    this.map.on('load', function () {
      addLayers();
    });
  }
});
