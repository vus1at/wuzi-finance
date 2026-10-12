import request from '@/utils/request'

export interface InitialBalance {
  id: number
  ytd_purchase_amount: number
  ytd_supply_amount: number
  ytd_payment_amount: number
  ytd_receipt_amount: number
  ytd_profit_amount: number
  ytd_supply_quantity: number
  cum_purchase_amount: number
  cum_supply_amount: number
  cum_payment_amount: number
  cum_receipt_amount: number
  cum_payment_ratio: number
  cum_receipt_ratio: number
  updated_at?: string
}

export const getInitialBalanceApi = () =>
  request.get<any, InitialBalance>('/initial-balance')

export const updateInitialBalanceApi = (data: Omit<InitialBalance, 'id' | 'updated_at'>) =>
  request.put<any, InitialBalance>('/initial-balance', data)