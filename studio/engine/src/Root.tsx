import React from 'react';
import { Composition } from 'remotion';
import { PipTest } from './PipTest';
import { TitleCard } from './TitleCard';
export const Root: React.FC = () => (
  <>
  <Composition id="TitleCard" component={TitleCard} durationInFrames={72} fps={24} width={1280} height={720} />
  <Composition id="PipTest" component={PipTest} durationInFrames={72} fps={24} width={1920} height={1080} />
  </>
);
