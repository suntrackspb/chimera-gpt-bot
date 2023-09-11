import React from 'react';
import CardsList from "./CardsList/CardsList.jsx";
import Header from "./Header.jsx";

const App = () => {
  return (
    <>
      <Header/>
      <main>
        <CardsList/>
      </main>
    </>
  );
};

export default App;