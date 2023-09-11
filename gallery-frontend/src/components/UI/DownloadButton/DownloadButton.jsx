import React from 'react';
import styles from "./DownloadButton.module.css";

const DownloadButton = ({link, name}) => {
  return (
    <a href={link} download={name} target='_blank' rel='noreferrer'>
      <svg className={styles.icon} xmlns="http://www.w3.org/2000/svg" width="40px" height="40px" viewBox="0 0 24 24">
        <g>
          <path id="Vector" d="M6 21H18M12 3V17M12 17L17 12M12 17L7 12" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
        </g>
      </svg>
    </a>
  );
};

export default DownloadButton;