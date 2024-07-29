import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'keyValue',
  standalone: true
})
export class KeyValuePipe implements PipeTransform {

  transform(value: any, ...args: unknown[]): any {
    if (!value) return [];
    return Object.keys(value).map(key => ({ key, value: value[key] }));
  }

}
