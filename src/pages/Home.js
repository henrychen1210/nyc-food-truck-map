import { getDocs, collection, deleteDoc, doc, query, where } from "firebase/firestore";
import { auth, db } from "../firebase-config";
import { useNavigate, createSearchParams, useLocation } from "react-router-dom";

import React, { useRef, useEffect, useState } from 'react';
import mapboxgl from '!mapbox-gl'; // eslint-disable-line import/no-webpack-loader-syntax
import '../App.css';

let lineData = require('../json/Subway_Lines.json');
let stops = require('../json/Subway_Stations.json');

mapboxgl.accessToken = process.env.REACT_APP_MAPBOX_TOKEN;

function Home({ isAuth }) {
  const [postLists, setPostList] = useState([]);
  const postsCollectionRef = collection(db, "posts");

  const mapContainer = useRef(null);
  const map = useRef(null);
  const [lng] = useState(-74.02);
  const [lat] = useState(40.74);
  const [zoom] = useState(12.3);
  const [stopdetailContent, setstopdetailContent] = useState(null);
  const [isHidden, setIsHidden] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  //http://web.mta.info/developers/resources/line_colors.html
  const colorMap = {
    A: "#0039A6",
    B: "#FF6319",
    G: "#6CBE45",
    J: "#996633",
    L: "#A7A9AC",
    N: "#FCCC0A",
    S: "#808183",
    "1": "#EE352E",
    "4": "#00933C",
    "7": "#B933AD"
  };

  const linesMap = {};
  lineData.features.map(
    line => (linesMap[line.properties.name] = line.properties.rt_symbol)
  );

  const colorStops = Object.keys(linesMap).map(key => [
    key,
    colorMap[linesMap[key]]
  ]);

  const maxBounds = stops.features.reduce(
    (acc, stop) => {
      const [[swLon, swLat], [neLon, neLat]] = acc;
      const [lon, lat] = stop.geometry.coordinates;
      return [
        [Math.min(swLon, lon), Math.min(swLat, lat)],
        [Math.max(neLon, lon), Math.max(neLat, lat)]
      ];
    },
    [[lng, lat], [lng, lat]]
  );

  const deletePost = async (id) => {
    const postDoc = doc(db, "posts", id);
    await deleteDoc(postDoc);
    getPosts("");
  };
  
  const editPost = async (id) => {
    // Edit post .........
    const postID = id;
    navigate({
      pathname: "/editpost",
      search: createSearchParams({
        postID: postID
      }).toString()
    });
  };
  
  const getPosts = async (station) => {
    console.log(station.toString())
    if(station === ""){
      const data = await getDocs(postsCollectionRef);
      setPostList(data.docs.map((doc) => ({ ...doc.data(), id: doc.id })));
    }
    else{
      const data = await getDocs(query(postsCollectionRef, where("station", "==", station.toString())));
      setPostList(data.docs.map((doc) => ({ ...doc.data(), id: doc.id })));
    }
  };

  useEffect(() => {
    if (map.current) return; // initialize map only once
    else if (!mapboxgl.supported()) {
      alert("Your browser does not support Mapbox GL");
    }
    else{
      map.current = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/dark-v9',
        center: [lng, lat],
        zoom: zoom,
        maxBounds: [
          [maxBounds[0][0] - 0.2, maxBounds[0][1] - 0.2],
          [maxBounds[1][0] + 0.2, maxBounds[1][1] + 0.2]
        ]
      });

      map.current.addControl(new mapboxgl.NavigationControl(), "top-right");
      
      for (const feature of stops.features) {
        // create a HTML element for each feature
        const el = document.createElement('div');
        el.className = 'marker';
        const line_className = {
          "A": "A",
          "C": "A",
          "E": "A",
          "B": "B",
          "D": "B",
          "F": "B",
          "M": "B",
          "G": "G",
          "J": "J",
          "Z": "J",
          "L": "L",
          "N": "N",
          "Q": "N",
          "W": "N",
          "R": "N",
          "S": "S",
          "1": "one",
          "2": "one",
          "3": "one",
          "4": "four",
          "5": "four",
          "6": "four",
          "7": "seven"
        };

        
        const lineArray = feature.properties.line.split("-");
        const div_line = document.createElement('div');
        const stop_name = document.createElement('p');
        
        div_line.className = "stopDetail";
        
        for (const label of lineArray) {
          if (label.includes("Express")) 
            continue
          const span = document.createElement('span');
          span.className = line_className[label];
          span.append(label);
          div_line.append(span);
        } 

        stop_name.append(feature.properties.name)
        div_line.append(stop_name)

        // make a marker for each feature and add to the map
        new mapboxgl.Marker(el)
                    .setLngLat(feature.geometry.coordinates)
                    .addTo(map.current)
                    .getElement()
                    .addEventListener("click", () => {
                      setstopdetailContent(`${div_line.outerHTML}`);
                      setIsHidden(!isHidden);
                      getPosts(feature.properties.name);
                    });
      }
      
  
      map.current.on("load", function() {
        map.current.addLayer({
          id: "trips",
          type: "line",
          source: {
            type: "geojson",
            data: lineData
          },
          layout: {
            "line-cap": "round",
            "line-join": "round"
          },
          paint: {
            "line-color": {
              property: "name",
              type: "categorical",
              stops: colorStops
            },
            "line-width": {
              base: 1,
              stops: [[9, 1], [11, 1], [13, 5], [15, 10]]
            }
          }
        });
        
        map.current.addLayer({
          id: "stations",
          source: {
            type: "geojson",
            data: stops
          },
          type: "circle",
          paint: {
            "circle-radius": {
              base: 1,
              stops: [[9, 0], [12, 0], [13, 5], [15, 10]]
            },
            "circle-color": "white",
            "circle-stroke-color": "black",
            "circle-stroke-width": {
              base: 1,
              stops: [[9, 0], [12, 0], [13, 1], [15, 2]]
            }
          }
        });
        

        map.current.addLayer({
          id: "stations-label",
          source: "stations",
          type: "symbol",
          paint: {
            "text-color": "white",
            "text-halo-color": "black",
            "text-halo-width": 1,
            "text-halo-blur": 4
          },
          layout: {
            "text-font": ["Open Sans Regular"],
            "text-field": "{name} ({line})",
            "text-size": {
              base: 12,
              stops: [[9, 0], [12, 0], [14, 12], [17, 20]]
            },
            "text-anchor": "right",
            "text-offset": [-1.5, 0]
          }
        });
      });
    }
    getPosts("");
  });

  useEffect(() => {
    if (!location.state?.showAll) {
      return;
    }

    setstopdetailContent(null);
    setIsHidden(false);

    getDocs(collection(db, "posts")).then((data) => {
      setPostList(data.docs.map((doc) => ({ ...doc.data(), id: doc.id })));
    });

    // Clear one-time navigation state so station selection is not reset again.
    navigate(location.pathname, { replace: true, state: {} });
  }, [location.state?.showAll, location.pathname, navigate]);

  return (
    <>
      <div ref={mapContainer} className="map-container" />
      <div className="header-wrap">
          <header>
              <h1>NYC Food Truck Map</h1>
              <div className={`lines ${isHidden ? 'hidden' : ''}`}>
                  <span className="A">A</span>
                  <span className="A">C</span>
                  <span className="A">E</span>
                  <span className="B">B</span>
                  <span className="B">D</span>
                  <span className="B">F</span>
                  <span className="B">M</span>
                  <span className="G">G</span>
                  <span className="J">J</span>
                  <span className="J">Z</span>
                  <span className="L">L</span>
                  <span className="N">N</span>
                  <span className="N">Q</span>
                  <span className="N">W</span>
                  <span className="N">R</span>
                  <span className="S">S</span>
                  <span className="one">1</span>
                  <span className="one">2</span>
                  <span className="one">3</span>
                  <span className="four">4</span>
                  <span className="four">5</span>
                  <span className="four">6</span>
                  <span className="seven">7</span>
              </div>

              <div dangerouslySetInnerHTML={{ __html: stopdetailContent }}></div>

              <div className="homePage">
                {postLists.map((post) => {
                  return (
                    <div className="post" key={post.id}>
                      <div className="postHeader">
                        <div className="title">
                          <h1> {post.title}  |  {post.station}</h1>
                          
                        </div>
                        <div className="editPost">
                          {isAuth && post.author.id === auth.currentUser.uid && (
                            <button
                              onClick={() => {
                                editPost(post.id);
                              }}
                            >
                              <img src="./edit.png" alt="" />
                            </button>
                          )}
                        </div>
                        <div className="deletePost">
                          {isAuth && post.author.id === auth.currentUser.uid && (
                            <button
                              onClick={() => {
                                deletePost(post.id);
                              }}
                            >
                              <img src="./trash.png" alt="" />
                            </button>
                          )}
                        </div>
                      </div>

                      <div className="postTextContainer"> {post.postText} </div>

                      <h3>@{post.author.name}, {new Date(post.date.seconds * 1000 + post.date.nanoseconds / 1000000).toDateString()}</h3>
                        
                    </div>
                  );
                })}
              </div>
          </header>
      </div>
    </>

    
  );
}

export default Home;