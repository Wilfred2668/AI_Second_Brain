import React, { useState } from 'react';
import styled from 'styled-components';

import find from './find.svg';
import smile from './smile.svg';

function Search({ className, goMain, onSearch, query }) {
  const [value, setValue] = useState(query);
  const [tag, setTag] = useState('All');
  function onChange(e) {
    setValue(e.target.value);
  }
  function onClick() {
    onSearch(value);
  }
  function onKeyDown(e) {
    if (e.key !== 'Enter') return;
    onSearch(value);
  }
  function renderTags() {
    return 'All,Maps,Images,News,Videos,More'.split(',').map(tagName => (
      <div
        onClick={() => setTag(tagName)}
        className={`tag ${tagName === tag ? 'active' : ''}`}
        key={tagName}
      >
        {tagName}
      </div>
    ));
  }
  return (
    <div className={className}>
      <section className="content">
        <iframe
          src={`https://www.google.com/search?q=${encodeURIComponent(query)}&igu=1`}
          width="100%"
          height="600"
          frameBorder="0"
          title="Google Search Results"
        />
      </section>
      <footer>
        <section className="upper">
          <div className="footer-items left">
            <div className="item">India</div>
          </div>
        </section>
        <section className="lower">
          <div className="footer-items left">
            <div className="item">Help</div>
            <div className="item">Send feedback</div>
            <div className="item">Privacy</div>
            <div className="item">Terms</div>
          </div>
        </section>
      </footer>
    </div>
  );
}

export default styled(Search)`
  height: 100%;
  background: white;
  position: relative;
  
  .content {
    height: calc(100% - 83px);
    
    iframe {
      width: 100%;
      height: 100%;
      border: none;
    }
  }
  
  footer {
    position: absolute;
    bottom: 0;
    width: 100%;
    height: 83px;
    border-top: 1px solid rgba(0, 0, 0, 0.07);
    background-color: rgba(0, 0, 0, 0.05);
    .upper {
      position: relative;
      color: rgba(0, 0, 0, 0.54);
      width: 100%;
      font-size: 15px;
      padding-bottom: 2px;
      height: 50%;
    }
    .lower {
      position: relative;
      border-top: 1px solid rgba(0, 0, 0, 0.07);
      height: 50%;
      color: rgb(95, 99, 104);
      font-size: 13px;
      width: 100%;
      .item {
        cursor: pointer;
      }
      .item:hover {
        text-decoration: underline;
      }
    }
    .footer-items {
      height: 100%;
      display: flex;
      align-items: center;
      padding-left: 150px;
      position: relative;
    }
    .left .item {
      margin-right: 27px;
    }
  }
`;
