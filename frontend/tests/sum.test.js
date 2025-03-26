const base_dir = '../';
const sum = require(base_dir + 'sum');

test('adds 1 + 2 to equal 3', () => {
    // Dummy comment change to test githook
    expect(sum(1, 2)).toBe(3);
})