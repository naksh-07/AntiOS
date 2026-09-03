import { describe, it, expect } from 'vitest';
import { greet } from '../src/index';

describe('greet', () => {
  it('greets correctly', () => {
    expect(greet('World')).toBe('Hello, World!');
  });
});
