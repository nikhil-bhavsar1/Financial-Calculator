import { TermMapping } from '../../types/terminology';

export const MARKET_DATA_TERMS: TermMapping[] = [
    {
        id: 'current_market_price',
        category: 'Current Market Price',
        key: 'current_market_price',
        label: 'Current Market Price',
        keywords_indas: ['market price', 'current share price', 'stock price', 'cmp'],
        keywords_gaap: ['market price', 'current share price', 'stock price'],
        keywords_ifrs: ['market price', 'current share price', 'stock price'],
    }
];
