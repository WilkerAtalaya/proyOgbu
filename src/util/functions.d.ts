declare module '@/util/functions' {
  export function dateFormatV1(value: string | number | Date): string;
  export function currentDate(): string;
  export function dateFormatDB(fecha: string): string;
  export function dateFormatV2(fecha: string): string;
  export function dateFormatV3(value: string | number | Date): string;
  export function dateFormatISO(value: string | number | Date): string;
}