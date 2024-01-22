/** Indicates whether the model is ready to use. */
export enum ModelStatus {

  /** Model is still loading and not ready. */
  LOADING,

  /** Model is ready to use for preidictions. */
  READY
}

/** Update event from the model worker to the UI. */
export interface ModelEvent {

  /** {@link ModelStatus} */
  status: ModelStatus,

  /**
   * If the status is {@link ModelStatus.LOADING}, this field indicates the
   * loading progress.
   */
  progressInPercent: number | undefined
}
