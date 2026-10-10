import { Composition } from "remotion";
import { AnuncioF, durationF } from "./AnuncioF";
import { AnuncioG, durationG } from "./AnuncioG";

const FPS = 30;

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="AnuncioF-Crecer"
        component={AnuncioF}
        durationInFrames={Math.ceil(durationF * FPS)}
        fps={FPS}
        width={1080}
        height={1920}
      />
      <Composition
        id="AnuncioG-MarketingAMano"
        component={AnuncioG}
        durationInFrames={Math.ceil(durationG * FPS)}
        fps={FPS}
        width={1080}
        height={1920}
      />
    </>
  );
};
