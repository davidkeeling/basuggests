import React from 'react';
import $ from 'jquery';

function dismiss (event) {
  event.preventDefault();
  event.stopPropagation();
  const el = $(event.target).closest('.hint');
  $(el).animate(
    { opacity: 0 },
    'linear',
    () => {
      $(el).css('display', 'none');
    }
  );
}

export default function Hint(props) {
  return (
    <div className="hint" onClick={dismiss} title="Dismiss tip">
      <div>{props.text}</div>
      <div className="arrow-up" />
    </div>
  );
}
