"use client"

import React from 'react';

import Modal from 'react-bootstrap/Modal';
import ProgressBar from 'react-bootstrap/ProgressBar';

/** Component properties for {@link Progress}. */
interface IProgressProperties {

  /** Progress in percent to display. */
  percentage: number,

  /** Indicates whether the progress indicator should be displayed. */
  visible: boolean
}

/**
 * Modal dialog progress component.
 * 
 * @param props {@link IProgressProperties}
 * @returns Modal progress dialog.
 */
const Progress = (props: IProgressProperties) => {
  return props.visible && <div className="block modal show">
    <Modal.Dialog>
      <Modal.Header>
        <Modal.Title>Loading AI model...</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <ProgressBar animated now={props.percentage} />
      </Modal.Body>
    </Modal.Dialog>
  </div>
};

export default Progress;
