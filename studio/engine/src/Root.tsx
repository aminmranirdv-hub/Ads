import React from 'react';
import { Composition } from 'remotion';
import { PipTest } from './PipTest';
export const Root: React.FC = () => (
  <Composition id="PipTest" component={PipTest} durationInFrames={72} fps={24} width={1920} height={1080} />
);
