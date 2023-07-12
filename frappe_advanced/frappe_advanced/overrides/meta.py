from __future__ import unicode_literals
import frappe
from frappe import _

from frappe.model.meta import Meta
from frappe.utils import cast

def apply_property_setters(self):
    """
    Property Setters are set via Customize Form. They override standard properties
    of the doctype or its child properties like fields, links etc. This method
    applies the customized properties over the standard meta object
    """
    if not frappe.db.table_exists("Property Setter"):
        return

    property_setters = frappe.db.sql(
        """select * from `tabProperty Setter` where
        doc_type=%s""",
        (self.name,),
        as_dict=1,
    )

    if not property_setters:
        return

    for ps in property_setters:
        if ps.doctype_or_field == "DocType":
            self.set(ps.property, cast(ps.property_type, ps.value))
        
        # Customized Code to either override or add to existing options
        elif ps.doctype_or_field == "DocField":
            for d in self.fields:
                if d.fieldname == ps.field_name:
                    #  store the new property setter options in a variable
                    options = ps.value
                    # if doctype field is a Select field 
                    # and Porperty Setter property field is options
                    # and new property setter check field is true (field_name: dont_replace)
                    # then options variable = original values + new values
                    if d.fieldtype == "Select" and ps.property=="options" and ps.dont_replace:
                        options = d.options + "\n" + ps.value
                    d.set(ps.property, cast(ps.property_type, options))
                    break

        elif ps.doctype_or_field == "DocType Link":
            for d in self.links:
                if d.name == ps.row_name:
                    d.set(ps.property, cast(ps.property_type, ps.value))
                    break

        elif ps.doctype_or_field == "DocType Action":
            for d in self.actions:
                if d.name == ps.row_name:
                    d.set(ps.property, cast(ps.property_type, ps.value))
                    break


def load_batches():
	Meta.apply_property_setters = apply_property_setters
	