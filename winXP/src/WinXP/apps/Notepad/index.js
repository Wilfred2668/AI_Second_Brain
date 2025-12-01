import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import API_URL from '../../../config';

import { WindowDropDowns } from 'components';
import dropDownData from './dropDownData';

export default function Notepad({ onClose, filePath, fileName }) {
  const [docText, setDocText] = useState('');
  const [wordWrap, setWordWrap] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);
  const [originalText, setOriginalText] = useState('');

  // Load file content when filePath is provided
  useEffect(() => {
    if (filePath && fileName) {
      setLoading(true);
      fetch(`${API_URL}/api/download/${fileName}`)
        .then(response => response.text())
        .then(text => {
          setDocText(text);
          setOriginalText(text);
          setHasChanges(false);
          setLoading(false);
        })
        .catch(error => {
          console.error('Error loading file:', error);
          setDocText('Error loading file content.');
          setLoading(false);
        });
    }
  }, [filePath, fileName]);

  // Track changes
  useEffect(() => {
    setHasChanges(docText !== originalText);
  }, [docText, originalText]);

  async function saveFile() {
    if (!fileName || !hasChanges || saving) return;
    
    setSaving(true);
    try {
      const response = await fetch(`${API_URL}/api/save/${encodeURIComponent(fileName)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'text/plain',
        },
        body: docText,
      });
      
      const result = await response.json();
      
      if (response.ok && result.success) {
        setOriginalText(docText);
        setHasChanges(false);
        console.log('File saved successfully');
      } else {
        console.error('Failed to save file:', result.error);
        alert(`Failed to save file: ${result.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error saving file:', error);
      alert('Error saving file: Network error');
    } finally {
      setSaving(false);
    }
  }

  function onClickOptionItem(item, event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }
    
    switch (item) {
      case 'Exit':
        onClose();
        break;
      case 'Save':
        event?.preventDefault();
        saveFile();
        break;
      case 'Word Wrap':
        setWordWrap(!wordWrap);
        break;
      case 'Time/Date':
        const date = new Date();
        setDocText(
          `${docText}${date.toLocaleTimeString()} ${date.toLocaleDateString()}`,
        );
        break;
      default:
    }
  }
  function onTextAreaKeyDown(e) {
    // handle tabs in text area
    if (e.which === 9) {
      e.preventDefault();
      e.persist();
      var start = e.target.selectionStart;
      var end = e.target.selectionEnd;
      setDocText(`${docText.substring(0, start)}\t${docText.substring(end)}`);

      // asynchronously update textarea selection to include tab
      // workaround due to https://github.com/facebook/react/issues/14174
      requestAnimationFrame(() => {
        e.target.selectionStart = start + 1;
        e.target.selectionEnd = start + 1;
      });
    }
  }

  return (
    <Div>
      <section className="np__toolbar">
        <WindowDropDowns items={dropDownData} onClickItem={onClickOptionItem} />
      </section>
      <StyledTextarea
        wordWrap={wordWrap}
        value={loading ? 'Loading file...' : docText}
        onChange={e => setDocText(e.target.value)}
        onKeyDown={(e) => {
          // Handle Ctrl+S for save
          if (e.ctrlKey && e.key === 's') {
            e.preventDefault();
            e.stopPropagation();
            saveFile();
            return false;
          }
          onTextAreaKeyDown(e);
        }}
        spellCheck={false}
        disabled={loading || saving}
        placeholder={saving ? 'Saving...' : ''}
        title={hasChanges ? 'File has unsaved changes' : 'File is saved'}
      />
    </Div>
  );
}

const Div = styled.div`
  height: 100%;
  background: linear-gradient(to right, #edede5 0%, #ede8cd 100%);
  display: flex;
  flex-direction: column;
  align-items: stretch;
  .np__toolbar {
    position: relative;
    height: 21px;
    flex-shrink: 0;
    border-bottom: 1px solid white;
  }
`;

const StyledTextarea = styled.textarea`
  flex: auto;
  outline: none;
  font-family: 'Lucida Console', monospace;
  font-size: 13px;
  line-height: 14px;
  resize: none;
  padding: 2px;
  ${props => (props.wordWrap ? '' : 'white-space: nowrap; overflow-x: scroll;')}
  overflow-y: scroll;
  border: 1px solid #96abff;
`;
