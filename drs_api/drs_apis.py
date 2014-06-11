from openerp.osv import fields, osv, orm



class drs_apis(osv.osv):
    _name = "drs.apis"
    _description = "APIs for Automating Order Process"
    sale_order_name='111-8209792-2360212'

    def sale_order_create(self, cr, uid, context=None):
        
        # parameters: customer, company ----------------------------------------------------------------------------------------------------
        print "sale_order_create called"
        product_id=2
        
        # create sale order ----------------------------------------------------------------------------------------------------------------
        sale_order_obj = self.pool.get('sale.order')
        values = {
            'name': self.sale_order_name,
            'shop_id': 1,
            'date_order':'2014-06-03',
            'partner_id': 5,
            'partner_invoice_id': 5,
            'partner_shipping_id': 5,
            'order_policy': 'manual',# ('manual', 'On Demand'),
            'pricelist_id': 1,
            'currency_id': 3, # USD
            'invoice_quantity': 'order', #('order', 'Ordered Quantities'),
        }
        sale_order_id = sale_order_obj.create(cr,uid,values)
        
        # create sale order line------------------------------------------------------------------------------------------------------------
        uom_id_of_products=self.pool.get('product.product').read(cr,uid,[product_id],['uom_id'])
        sale_order_line_obj = self.pool.get('sale.order.line')
        values = {
            'order_id': sale_order_id,
            'product_id':product_id,
            'name':'Temp Description',
            'price_unit': 50,
            'type':'make_to_stock',
            'product_uom_qty': 5,
            'product_uom': uom_id_of_products[0]['uom_id'][0],
            'state': 'draft',
        }
        sale_order_line_obj.create(cr,uid,values)
        
        # confirm this order ---------------------------------------------------------------------------------------------------------------
        sale_order_obj.action_button_confirm(cr,uid,[sale_order_id])

        res = {}
        print "sale_order_create called"
        return res
        
    def sale_order_cancel(self, cr, uid, context=None):
        sale_order_obj = self.pool.get('sale.order')
        sale_order_obj.action_cancel(cr, uid, ids)
        print "sale_order_cancel Called"

    def invoice_create(self,cr,uid):

        # Create DRAFT Invoice From Sale Order ---------------------------------------------------------------------------------------------
        sale_obj = self.pool.get('sale.order')
        sale_id = sale_obj.search(cr,uid,[('name','=',self.sale_order_name)])[0]
        sale_obj.manual_invoice(cr, uid, [sale_id])

        # Get the The Invoice --------------------------------------------------------------------------------------------------------------
        account_invoice_obj = self.pool.get('account.invoice')
        account_invoice_id = account_invoice_obj.search(cr,uid,[('origin','=',self.sale_order_name)])[0]

        # Set this DRAFT invoice to OPEN ---------------------------------------------------------------------------------------------------
        account_invoice_obj.action_date_assign( cr, uid, [account_invoice_id] )
        account_invoice_obj.action_move_create( cr, uid, [account_invoice_id] )
        account_invoice_obj.action_number( cr, uid,[account_invoice_id] )
        account_invoice_obj.invoice_validate( cr, uid,[account_invoice_id] )

        print "invoice_create Called"
        return {}

    def invoice_cancel(self, cr, uid, context=None):
        pass

    def invoice_register_payment(self, cr, uid, context=None):

        # Get the The Invoice ------------------------------------------------------------------------------------------------------------
        account_invoice_obj = self.pool.get('account.invoice')
        account_invoice_id = account_invoice_obj.search(cr,uid,[('origin','=',self.sale_order_name)])[0]

        # Register Payment -----------------------------------------------------------------------------------------------------------------
        account_voucher_obj = self.pool.get('account.voucher')
        account_voucher_obj.proforma_voucher( cr, uid, [account_invoice_id] )

    def invoice_refund(self, cr, uid, context=None):
        pass

    def products_deliver(self,cr,uid):
        stock_pick_obj = self.pool.get('stock.picking')
        picking_id = stock_pick_obj.search(cr,uid,[('origin','=',self.sale_order_name)])[0]
        stock_pick_obj.write(cr,uid,[picking_id],{'auto_picking':True,'move_type':'one'})
        stock_pick_obj.action_assign(cr, uid, [picking_id])
        return {};

    def products_deliver_cancel():
        pass

    def products_return():
        pass

    def customer_create(self, cr, uid, values):
        # Create Customer  ---------------------------------------------------------------------------------------------------------------
        # parameters: name, email, company, country
        print "customer_create called"
        partner = self.pool.get('res.partner')
        country_code = context.get('country_code',False)
        country_id = self.pool.get('res.country').search(cr,uid,[('code','=',country_code)])[0]
        if len( partner.search(cr,uid,[('name','=','Roger Chen')])) !=0:
            print "name exist"
            return
        partner.create(cr,uid,{'name':'Roger Chen','email':'roger.chen@kindminds.com', 'country_id':country_id})

class product_product(orm.Model):

    _inherit = "product.product"

    def call_sale_order_create(self, cr, uid, ids, context=None):
        return self.pool.get("drs.apis").sale_order_create(cr,uid)

    def call_sale_order_cancel():
        return self.pool.get("drs.apis").sale_order_cancel(cr,uid)

    def call_invoice_create(self, cr, uid, ids, context=None):
        return self.pool.get("drs.apis").invoice_create(cr,uid)

    def call_customer_create(self, cr, uid, ids, context=None):
        return self.pool.get("drs.apis").customer_create(cr,uid,values)

    def call_products_deliver(self, cr, uid, ids, context=None):
        return self.pool.get("drs.apis").products_deliver(cr,uid)

    def call_products_deliver_cancel(self, cr, uid, ids, context=None):
        return self.pool.get("drs.apis").products_deliver_cancel(cr,uid)

    def call_products_return(self, cr, uid, ids, context=None):
        return self.pool.get("drs.apis").products_return(cr,uid)

    def call_invoice_register_payment(self, cr, uid, ids, context=None):
        return self.pool.get("drs.apis").invoice_register_payment(cr,uid)

# invoice_obj = self.pool.get('account.invoice')
# values = {
#     'origin':self.sale_order_name,
#     'type': 'out_invoice',
#     'state':'draft', #'Draft'),('proforma','Pro-forma'),('proforma2','Pro-forma'),('open','Open'),('paid','Paid'),('cancel','Cancelled'),
#     'partner_id':5,
#     'account_id':5, # account receivable
#     'currency_id':3, # USD
#     'journal_id':1, # SAJ
#     'company_id':1,
# }
# invoice_id = invoice_obj.create(cr,uid,values)

# for record in partner.search(cr,uid,[]):
#     obj = partner.browse(cr,uid,[record])[0]
#     if obj.name=='Roger Chen':