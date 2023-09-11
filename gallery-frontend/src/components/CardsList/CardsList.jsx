import React from 'react';
import styles from './CardsList.module.css'
import Card from "../Card/Card.jsx";
import ImageModal from "../ImageModal/ImageModal.jsx";
import {useScrollPagination} from "../../hooks/";

const CardsList = () => {
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [selectedCard, setSelectedCard] = React.useState({});

  const limit = 12
  const {
    data,
    skip,
    isLast,
    handleScrollPagination
  } = useScrollPagination(() => getCards(skip, limit), 0, limit)


  React.useEffect(() => {
    !isLast
      ? document.addEventListener('scroll', handleScrollPagination)
      : document.removeEventListener('scroll', handleScrollPagination)
    return () => document.removeEventListener('scroll', handleScrollPagination)
  }, [isLast])

  const getCards = async (skip, limit) => {
    return await fetch(`https://sntrk.ru/api/images?limit=${limit}&skip=${skip}`)
  }

  const onImageClick = (card) => {
    setSelectedCard(card)
    setIsModalOpen(true)
  }

  const renderCards = () => {
    return data.map(({_id, ...card}) =>
      <Card key={_id} onImageClick={onImageClick} {...card}/>)
  }

  return (
    <div className={styles.grid}>
      {renderCards()}
      <ImageModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        {...selectedCard}
      />
    </div>
  );
};

export default CardsList;