import React from 'react';
import styles from './ImageModal.module.css'
import {IMAGES_PATH} from "../../utils/consts.js";
import DownloadButton from "../UI/DownloadButton/DownloadButton.jsx";

const ImageModal = ({isOpen, onClose, style, prompt, img_name}) => {
  const [shouldRender, setShouldRender] = React.useState(isOpen);
  const animation = {animation: `${isOpen ? 'fadeIn' : 'fadeOut'} .3s forwards`}

  React.useEffect(() => {
    isOpen && setShouldRender(true)
  }, [isOpen]);

  const onAnimationEnd = () => {
    !isOpen && setShouldRender(false)
  }

  const handleCloseOnEsc = e => {
    if (e.key === 'Escape') {
      onClose()
    }
  }

  React.useEffect(() => {
    isOpen
      ? document.addEventListener('keydown', handleCloseOnEsc)
      : document.removeEventListener('keydown', handleCloseOnEsc)
    return () => {
      document.removeEventListener('keydown', handleCloseOnEsc)
    }
  }, [isOpen]);

  return (
    <>
      {shouldRender && <div
        className={styles.modal}
        onClick={onClose}
        style={animation}
        onAnimationEnd={onAnimationEnd}
      >
        <div className={styles.content} onClick={e => e.stopPropagation()}>
          <DownloadButton link={`${IMAGES_PATH}${img_name}`} name={prompt}/>
          <img width={700} height={700} className={styles.image} src={`${IMAGES_PATH}/${img_name}`} alt={prompt}/>
          <p>
            <strong>Prompt:</strong> {prompt}
          </p>
          <p>
            <strong>Style:</strong> {style}
          </p>

        </div>
      </div>}
    </>
  );
};

export default ImageModal;