import React, { useState, useEffect } from "react";
import { getDoc, doc, updateDoc } from "firebase/firestore";
import { ref, uploadBytes, getDownloadURL, deleteObject } from "firebase/storage";
import { db, storage } from "../firebase-config";
import { useNavigate, useSearchParams } from "react-router-dom";

let stops = require('../json/Subway_Stations.json');

function EditPost({ isAuth }) {
  const [searchparams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [title, setTitle] = useState("");
  const [line, setLine] = useState("");
  const [station, setStation] = useState("");
  const [address, setAddress] = useState("");
  const [postText, setPostText] = useState("");
  const [imagesURL, setImagesURL] = useState([]);
  const [selectedImage, setSelectedImage] = useState([]);

  let navigate = useNavigate();
  const postID = searchparams.get("postID");
  const postDoc = doc(db, "posts", postID);

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

  const handleImageClick = (image) => {
    setSelectedImage(image);
  };

  const editPost = async () => {
    const date = new Date();
    let new_imagesURL = imagesURL;

    if(selectedImage != null){
      for (let i = 0; i < selectedImage.length; i++) {
        const file = selectedImage[i];
        const storageRef = ref(storage, 'images/' + file.name); // Adjust the storage reference path as per your requirement
        try {
          await uploadBytes(storageRef, file);
          const downloadURL = await getDownloadURL(storageRef);
          new_imagesURL.push(downloadURL);
          // Do something with the download URL, such as storing it in a database or displaying it to the user
        } catch (error) {
          // Handle any errors that occur during the upload process
          console.log('Error uploading file:', error);
        }
      }
    }
    console.log(new_imagesURL);
    setImagesURL(new_imagesURL);
    
    await updateDoc(postDoc, {
        line: line,
        postText: postText,
        station: station,
        address: address,
        title: title,
        date: date,
        imagesURL: imagesURL
    });
    navigate("/");
  };

  const deleteImage = async (index) => {
    const updatedList = imagesURL.filter((_, i) => i !== index);

    
    const filePath = imagesURL[index].split('/').pop().split('?')[0];
    const storageRef = ref(storage, filePath.replace( "%2F", "/"));

    try {
      await deleteObject(storageRef);
      console.log("File deleted successfully");
    } catch (error) {
      console.log("Error deleting file:", error);
    }
    
    setImagesURL(updatedList);

  };

  const handleImageChange = (event) => {
    setSelectedImage(event.target.files);
  };

  useEffect(() => {
    setLoading(true)

    if (!isAuth) {
      navigate("/login");
    }

    getDoc(postDoc)
      .then((docSnapshot) => {
        if (docSnapshot.exists()) {
          const postData = docSnapshot.data();
          setTitle(postData.title);
          setLine(postData.line);
          setStation(postData.station);
          setAddress(postData.address);
          setPostText(postData.postText);
          setImagesURL(postData.imagesURL);
          console.log(postData)
        } else {
          console.log("Document does not exist");
        }
      })
      .catch((error) => {
        console.log("Error retrieving document:", error);
      })
      .finally(() => {
        setLoading(false); // Set loading to false when the data is fetched
      });
  }, [isAuth, navigate, postDoc]);

  if (loading) {
    return <div>Loading...</div>; // Render a loading indicator while fetching the data
  }

  return (
    <div className="editPostPage">
      <div className="cpContainer">
        <h1>Edit Post</h1>

        <div className="inputGp">
          <label>Title:</label>
          <input
            placeholder="Title..."
            onChange={(event) => {
              setTitle(event.target.value);
            }}
            defaultValue={title}
          />
        </div>

        <div className="inputGp">
          <label>Line:</label>
          <select
            onChange={(event) => {
              setLine(event.target.value);
            }}
            defaultValue={line}
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
                    defaultValue={station}
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
                    defaultValue={station}
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
                    defaultValue={station}
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
                    defaultValue={station}
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
                    defaultValue={station}
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
                    defaultValue={station}
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
                    defaultValue={station}
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
                    defaultValue={station}
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
                    defaultValue={station}
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
                    defaultValue={station}
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
            defaultValue={address}
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
                defaultValue={postText}
            />
        </div>

        <div className="postImageContainer">
          {imagesURL.map((image) => (
            <div className="deletePost">
              <img
              src={image}
              alt=""
              className="postImage"
              onClick={() => handleImageClick(image)}
              key={image}
            />
              <button
                onClick={() => {
                  deleteImage(imagesURL.indexOf(image));
                }}
              >
                <img src="./trash.png" alt="" />
              </button>
            </div>
            
          ))}
        </div>

        <div className="uploadImage">
          <label htmlFor="fileInput" className="customButton">
            <span>Upload Images</span>
            <input type="file" id="fileInput" multiple onChange={handleImageChange} />
          </label>
        </div>

        <button onClick={editPost}>Submit Post</button>
      </div>
    </div>
  );
}

export default EditPost;
