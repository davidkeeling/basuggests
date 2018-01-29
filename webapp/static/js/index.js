import React from 'react';
import ReactDOM from 'react-dom';
import ActRecommender from './recommend';
import Hint from './hint';

function BASuggests (props) {
  return (
    <div>
      <header className="page_header">
        <h1>Browse Acts of Peace</h1>
        <p style={{ fontSize: 'smaller' }}>
          from <a href="https://www.billionacts.org" target="_blank">1 Billion Acts of Peace</a>
        </p>
        <div className="login">
          {props.user ? (
            <span>
              {props.user.picture && (
                <img src={props.user.picture} title={props.user.email} />
              )}
              <a href="/logout">Logout</a>
            </span>
          ) : (
            <span>
              <a href="/login">Login</a>
            </span>
          )}
          {!user && (
            <Hint text="Login with Google to save your likes" />
          )}
        </div>
      </header>

      <ActRecommender user={user} />

      <footer>
        <div className="column">
          <div>
            David Keeling
          </div>
          <div>
            <a href="https://github.com/davidkeeling/basuggests" target="_blank">
              <img src="/static/img/github.png" style={{ height: "1em", verticalAlign: "middle" }} />
              <span style={{ paddingLeft: ".25em" }}>basuggests on github</span>
            </a>
          </div>
        </div>
        <div className="column">
          <div>
            <a href="http://www.peacejam.org" target="_blank">The PeaceJam Foundation</a>
          </div>
          <div>
            <a href="http://www.billionacts.org" target="_blank">1 Billion Acts of Peace</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

ReactDOM.render(
  <BASuggests user={user} />,
  document.getElementById('app')
);
