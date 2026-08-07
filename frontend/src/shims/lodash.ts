export const sortBy = (arr: any[], ...args: any[]) => arr.sort();
export const throttle = (fn: any, wait: number) => fn;
export const upperFirst = (str: string) => str ? str.charAt(0).toUpperCase() + str.slice(1) : '';
export const some = (arr: any[], predicate: any) => arr.some(predicate);
export const range = (start: number, end?: number, step: number = 1) => {
  if (end === undefined) { end = start; start = 0; }
  const result = [];
  for (let i = start; i < end; i += step) result.push(i);
  return result;
};
export const sumBy = (arr: any[], iteratee: any) => arr.reduce((sum, item) => sum + (typeof iteratee === 'function' ? iteratee(item) : item[iteratee]), 0);
export const uniqBy = (arr: any[], iteratee: any) => {
  const seen = new Set();
  return arr.filter(item => {
    const val = typeof iteratee === 'function' ? iteratee(item) : item[iteratee];
    if (seen.has(val)) return false;
    seen.add(val);
    return true;
  });
};
export default { sortBy, throttle, upperFirst, some, range, sumBy, uniqBy };
