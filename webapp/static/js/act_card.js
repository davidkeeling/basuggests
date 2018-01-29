import React from 'react';
import Hint from './hint';

export default function ActCard(props) {
  const { act_data } = props;
  const fontSize = act_data.name.length > 50 ? '.75em' : '1em';
  return (
    <div className="act_card" onClick={props.expand_act(act_data)}>
      <header style={{ fontSize }}>
        <h4><div>{act_data.name}</div></h4>
      </header>
      <div className="description">
        <div className="inner">
          <p>{act_data.description}</p>
        </div>
      </div>

      {props.show_expand_hint && (
        <div style={{ position: 'absolute', bottom: '-.5em', right: 0 }}>
          <Hint text="Click an act to expand" />
        </div>
      )}
    </div>
  );
}
