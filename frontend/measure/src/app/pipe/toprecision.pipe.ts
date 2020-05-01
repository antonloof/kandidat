import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'toprecision',
})
export class ToprecisionPipe implements PipeTransform {
  transform(value: number, digits?: number): string {
    if (!value && value !== 0) {
      return '';
    }
    if (!digits) {
      digits = 4;
    }
    return `${parseFloat(value.toPrecision(digits))}`;
  }
}
