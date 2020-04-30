import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'sheetResistance',
})
export class SheetResistancePipe implements PipeTransform {
  transform(value: number): string {
    if (!value && value !== 0) {
      return '';
    }
    return `${parseFloat(value.toPrecision(4))}`;
  }
}
