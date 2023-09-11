import React from 'react';
import {IMAGES_PATH} from "../../utils/consts.js";
import styles from './Card.module.css'
import DownloadButton from "../UI/DownloadButton/DownloadButton.jsx";

const Card = ({style, prompt, img_name, onImageClick}) => {
  const onClick = () => {
    onImageClick({style, prompt, img_name})
  }

  return (
    <div className={styles.card}>
      <DownloadButton link={`${IMAGES_PATH}${img_name}`} name={prompt}/>
      <img onClick={onClick} className={styles.image} src={`${IMAGES_PATH}/${img_name}`} alt=""/>
      <div className={styles.textContainer}>
        <p className={styles.prompt}>
          <strong>Prompt:</strong> {prompt}
        </p>
        <p>
          <strong>Style:</strong> {style}
        </p>
      </div>
    </div>
  );
};

export default Card;