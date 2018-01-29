import React from 'react';
import Hint from './hint';

export default function Act(props) {
  const { act_data } = props;
  const fontSize = act_data.name.length > 50 ? '1.25em' : '1.5em';
  return (
    <div className="act">
      <header>
        <h2 style={{ fontSize }}><div>{act_data.name}</div></h2>
      </header>
      <div className="description">
        <figure className="love_button">
          <img
            src={props.is_loved ? '/static/img/symbol-color.png' : 'static/img/symbol-grey.png'}
            onClick={props.love_act}
          />
          {props.show_like_hint && (
            <Hint text="Add to your likes" />
          )}
        </figure>
        {act_data.description.split('\n\r').map((p, i) => (
          <p key={i}>{p}</p>
        ))}
      </div>
      <div className="link">
        <a target="_blank" href={`https://www.billionacts.org/act/${act_data.projectID}`}>
          See on billionacts.org
        </a>
      </div>
    </div>
  );
}
