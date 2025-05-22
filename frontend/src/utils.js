import { EventSourceParserStream } from 'eventsource-parser/stream';

export async function* parseSSEStream(stream) {
  const sseReader = stream
    .pipeThrough(new TextDecoderStream())
    .pipeThrough(new EventSourceParserStream())
    .getReader();
  
  while (true) {
    const { done, value } = await sseReader.read();
    if (done) break;
    yield value.data;
  }
}