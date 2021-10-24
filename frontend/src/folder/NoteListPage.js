import React from "react";
import otess from "../assets/data";
import Listitem from "../components/Listitem";
const NoteListPage = () => {
  return (
    <div>
      <div div className="notes-list">
        {" "}
        {otess.map((otessu) => (
          <p> {otessu.body} </p>
        ))}
      </div>
    </div>
  );
};

export default NoteListPage;
