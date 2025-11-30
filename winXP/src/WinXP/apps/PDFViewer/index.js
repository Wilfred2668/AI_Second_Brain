import React from 'react';
import styled from 'styled-components';
import { WindowDropDowns } from 'components';

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
      { text: 'Select All', disabled: true },
      { text: 'Find...', disabled: true },
    ],
  },
  {
    text: 'View',
    items: [
      { text: 'Zoom In', disabled: true },
      { text: 'Zoom Out', disabled: true },
      { text: 'Actual Size', disabled: true },
      { text: 'Fit Page', disabled: true },
    ],
  },
  {
    text: 'Help',
    items: [
      { text: 'About PDF Viewer', disabled: true },
    ],
  },
];

function PDFViewer({ onClose, filePath, fileName }) {
  function onClickOptionItem(item) {
    switch (item) {
      case 'Close':
        onClose();
        break;
      default:
    }
  }

  return (
    <Div>
      <section className="pdf__content">
        <div className="pdf__viewer">
          {fileName ? (
            <iframe
              src={`http://localhost:8001/api/download/${encodeURIComponent(fileName)}`}
              width="100%"
              height="100%"
              title={`PDF Viewer - ${fileName}`}
              frameBorder="0"
              style={{ border: 'none' }}
            />
          ) : (
            <div className="pdf__placeholder">
              <div>No PDF selected</div>
              <div>Please select a PDF file to view</div>
            </div>
          )}
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

  .pdf__toolbar {
    position: relative;
    display: flex;
    align-items: center;
    line-height: 100%;
    height: 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.7);
    flex-shrink: 0;
  }

  .pdf__options {
    height: 23px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    border-right: 1px solid rgba(0, 0, 0, 0.1);
    padding: 1px 0 1px 2px;
    border-left: 0;
    flex: 1;
  }

  .pdf__content {
    flex: 1;
    display: flex;
    background: white;
    position: relative;
  }

  .pdf__viewer {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .pdf__placeholder {
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

  iframe {
    border: none;
  }
`;

export default PDFViewer;