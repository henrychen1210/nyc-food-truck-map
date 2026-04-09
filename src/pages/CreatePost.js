import React, { useState, useEffect } from "react";
import { addDoc, collection } from "firebase/firestore";
import { db, auth } from "../firebase-config";
import { useNavigate } from "react-router-dom";

let stops = require('../json/Subway_Stations.json');

function CreatePost({ isAuth }) {

  const [title, setTitle] = useState("");
  const [line, setLine] = useState("A");
  const [station, setStation] = useState("");
  const [postText, setPostText] = useState("");
  const [address, setAddress] = useState("");

  const postsCollectionRef = collection(db, "posts");
  let navigate = useNavigate();

  let stations_ace = [];
  let stations_bdfm = [];
  let stations_g = [];
  let stations_jz = [];
  let stations_l = [];
  let stations_nqwr = [];
  let stations_s = [];
  let stations_123 = [];
  let stations_456 = [];
  let stations_7 = [];

  stops.features.map(
    stop => {
      if((stop.properties.line?.includes('A') || stop.properties.line?.includes('C') || stop.properties.line?.includes('E')) && !stations_ace.includes(stop.properties.name)){
        stations_ace.push(stop.properties.name);
      }
      else if((stop.properties.line?.includes('B') || stop.properties.line?.includes('D') || stop.properties.line?.includes('F') || stop.properties.line?.includes('M')) && !stations_bdfm.includes(stop.properties.name)){
        stations_bdfm.push(stop.properties.name);
      }
      else if(stop.properties.line?.includes('G') && !stations_g.includes(stop.properties.name)){
        stations_g.push(stop.properties.name);
      }
      else if((stop.properties.line?.includes('J') || stop.properties.line?.includes('Z')) && !stations_jz.includes(stop.properties.name)){
        stations_jz.push(stop.properties.name);
      }
      else if(stop.properties.line?.includes('L') && !stations_l.includes(stop.properties.name)){
        stations_l.push(stop.properties.name);
      }
      else if((stop.properties.line?.includes('N') || stop.properties.line?.includes('Q') || stop.properties.line?.includes('W') || stop.properties.line?.includes('R')) && !stations_nqwr.includes(stop.properties.name)){
        stations_nqwr.push(stop.properties.name);
      }
      else if(stop.properties.line?.includes('S') && !stations_s.includes(stop.properties.name)){
        stations_s.push(stop.properties.name);
      }
      else if((stop.properties.line?.includes('1') || stop.properties.line?.includes('2') || stop.properties.line?.includes('3')) && !stations_123.includes(stop.properties.name)){
        stations_123.push(stop.properties.name);
      }
      else if((stop.properties.line?.includes('4') || stop.properties.line?.includes('5') || stop.properties.line?.includes('6')) && !stations_456.includes(stop.properties.name)){
        stations_456.push(stop.properties.name);
      }
      else if(stop.properties.line?.includes('7') && !stations_7.includes(stop.properties.name)){
        stations_7.push(stop.properties.name);
      }
      return null;
    }
  );

  stations_ace.sort();
  stations_bdfm.sort();
  stations_g.sort();
  stations_jz.sort();
  stations_l.sort();
  stations_nqwr.sort();
  stations_s.sort();
  stations_123.sort();
  stations_456.sort();
  stations_7.sort();

  const createPost = async () => {
    const date = new Date();

    await addDoc(postsCollectionRef, {
      title,
      date,
      line,
      station,
      address,
      postText,
      imagesURL: [],
      author: { 
        name: auth.currentUser.displayName, 
        id: auth.currentUser.uid 
      },
    });

    navigate("/");
  };

  useEffect(() => {
    if (!isAuth) {
      navigate("/login");
    }
  }, [isAuth, navigate]);

  return (
    <div className="createPostPage">
      <div className="cpContainer">
        <h1>Create A Post</h1>


        <div className="inputGp">
          <label> Title:</label>
          <input
            placeholder="Title..."
            onChange={(event) => {
              setTitle(event.target.value);
            }}
          />
        </div>

        <div className="inputGp">
          <label> Line:</label>
          <select
                  onChange={(event) => {
                    setLine(event.target.value);
                  }}
                  >
            <option value="A">A, C, E</option>
            <option value="B">B, D, F, M</option>
            <option value="G">G</option>
            <option value="J">J, Z</option>
            <option value="L">L</option>
            <option value="N">N, Q, W, R</option>
            <option value="S">S</option>
            <option value="one">1, 2, 3</option>
            <option value="four">4, 5, 6</option>
            <option value="seven">7</option>
          </select>
        </div>

        <div className="inputGp">
          <label> Station:</label>
            {line === "A" ? (
                <select
                        onChange={(event) => {
                          setStation(event.target.value);
                        }}
                        >
                  {stations_ace.map((station, index) => (
                    <option key={index} value={station}>
                    {station}
                    </option>
                  ))}
                </select>
            
            ) : line === "B" ? (
                <select
                        onChange={(event) => {
                          setStation(event.target.value);
                        }}
                        >
                  {stations_bdfm.map((station, index) => (
                    <option key={index} value={station}>
                    {station}
                    </option>
                  ))}
                </select>
            ) : line === "G" ? (
                <select
                        onChange={(event) => {
                          setStation(event.target.value);
                        }}
                        >
                  {stations_g.map((station, index) => (
                    <option key={index} value={station}>
                    {station}
                    </option>
                  ))}
                </select>
            ) : line === "J" ? (
                <select
                        onChange={(event) => {
                          setStation(event.target.value);
                        }}
                        >
                  {stations_jz.map((station, index) => (
                    <option key={index} value={station}>
                    {station}
                    </option>
                  ))}
                </select>
            ) : line === "L" ? (
                <select
                        onChange={(event) => {
                          setStation(event.target.value);
                        }}
                        >
                  {stations_l.map((station, index) => (
                    <option key={index} value={station}>
                    {station}
                    </option>
                  ))}
                </select>
            ) : line === "N" ? (
                <select
                        onChange={(event) => {
                          setStation(event.target.value);
                        }}
                        >
                  {stations_nqwr.map((station, index) => (
                    <option key={index} value={station}>
                    {station}
                    </option>
                  ))}
                </select>
            ) : line === "S" ? (
                <select
                        onChange={(event) => {
                          setStation(event.target.value);
                        }}
                        >
                  {stations_s.map((station, index) => (
                    <option key={index} value={station}>
                    {station}
                    </option>
                  ))}
                </select>
            ) : line === "one" ? (
                <select
                        onChange={(event) => {
                          setStation(event.target.value);
                        }}
                        >
                  {stations_123.map((station, index) => (
                    <option key={index} value={station}>
                    {station}
                    </option>
                  ))}
                </select>
            ) : line === "four" ? (
                <select
                        onChange={(event) => {
                          setStation(event.target.value);
                        }}
                        >
                  {stations_456.map((station, index) => (
                    <option key={index} value={station}>
                    {station}
                    </option>
                  ))}
                </select>
            ) : line === "seven" ? (
                <select
                        onChange={(event) => {
                          setStation(event.target.value);
                        }}
                        >
                  {stations_7.map((station, index) => (
                    <option key={index} value={station}>
                    {station}
                    </option>
                  ))}
                </select>
            ) : null}
        </div>

        <div className="inputGp">
          <label> Address:</label>
          <input
            placeholder="Address..."
            onChange={(event) => {
              setAddress(event.target.value);
            }}
          />
        </div>

        <div className="inputGp">
          <label> Review:</label>
          <textarea
            placeholder="Review..."
            onChange={(event) => {
              setPostText(event.target.value);
            }}
          />
        </div>
        
        <button onClick={createPost}> Submit Post</button>
      </div>
    </div>
  );
}

export default CreatePost;