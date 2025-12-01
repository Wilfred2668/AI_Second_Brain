import React, { useState } from 'react';
import styled from 'styled-components';
import { WindowDropDowns } from 'components';
import API_URL from '../../../config';

const dropDownData = [
  {
    text: 'File',
    items: [
      { text: 'Open...', disabled: true },
      { text: 'Print...', disabled: true },
      { type: 'separator' },
      { text: 'Close' },
    ],
  },
  {
    text: 'Edit',
    items: [
      { text: 'Copy', disabled: true },
      { text: 'Paste', disabled: true },
      { text: 'Rotate Right', disabled: true },
      { text: 'Rotate Left', disabled: true },
    ],
  },
  {
    text: 'View',
    items: [
      { text: 'Zoom In' },
      { text: 'Zoom Out' },
      { text: 'Actual Size' },
      { text: 'Best Fit' },
    ],
  },
  {
    text: 'Help',
    items: [
      { text: 'About Image Viewer', disabled: true },
    ],
  },
];

function ImageViewer({ onClose, filePath, fileName }) {
  const [zoom, setZoom] = useState(1);
  const [fitMode, setFitMode] = useState('best');

  function onClickOptionItem(item) {
    switch (item) {
      case 'Close':
        onClose();
        break;
      case 'Zoom In':
        setZoom(prev => Math.min(prev * 1.2, 5));
        setFitMode('none');
        break;
      case 'Zoom Out':
        setZoom(prev => Math.max(prev / 1.2, 0.1));
        setFitMode('none');
        break;
      case 'Actual Size':
        setZoom(1);
        setFitMode('none');
        break;
      case 'Best Fit':
        setFitMode('best');
        break;
      default:
    }
  }

  const imageStyle = {
    transform: fitMode === 'none' ? `scale(${zoom})` : 'none',
    maxWidth: fitMode === 'best' ? '100%' : 'none',
    maxHeight: fitMode === 'best' ? '100%' : 'none',
    transition: 'transform 0.2s ease',
  };

  return (
    <Div>
      <section className="image__content">
        <div className="image__viewer">
          {fileName ? (
            <iframe
              src={`${API_URL}/api/download/${encodeURIComponent(fileName)}`}
              width="100%"
              height="100%"
              title={`Image Viewer - ${fileName}`}
              frameBorder="0"
              style={{ 
                border: 'none',
                transform: `scale(${zoom})`,
                transformOrigin: 'top left'
              }}
            />
          ) : (
            <div className="image__placeholder">
              <div>No image selected</div>
              <div>Please select an image file to view</div>
            </div>
          )}
        </div>
      </section>
      <section className="image__status">
        <div className="status__text">
          {fileName && `${fileName} - ${Math.round(zoom * 100)}%`}
        </div>
      </section>
    </Div>
  );
}

const Div = styled.div`
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(to right, #edede5 0%, #ede8cd 100%);

  .image__toolbar {
    position: relative;
    display: flex;
    align-items: center;
    line-height: 100%;
    height: 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.7);
    flex-shrink: 0;
  }

  .image__options {
    height: 23px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    border-right: 1px solid rgba(0, 0, 0, 0.1);
    padding: 1px 0 1px 2px;
    border-left: 0;
    flex: 1;
  }

  .image__content {
    flex: 1;
    display: flex;
    background: #f0f0f0;
    position: relative;
    overflow: auto;
  }

  .image__viewer {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    box-sizing: border-box;
  }

  .image__placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #666;
    font-size: 14px;
    
    div:first-child {
      font-weight: bold;
      margin-bottom: 8px;
    }
  }

  .image__status {
    height: 24px;
    background: #e0e0e0;
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    display: flex;
    align-items: center;
    padding: 0 8px;
    font-size: 11px;
    color: #333;
  }

  img {
    cursor: grab;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    background: white;
    
    &:active {
      cursor: grabbing;
    }
  }
`;

export default ImageViewer;